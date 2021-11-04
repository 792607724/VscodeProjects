# coding=utf-8

import os
import sys
import subprocess
import threading
import time

import traceback
from datetime import datetime

import logger
from uiautomator import Device
from ConfigParser import ConfigParser
from common import Common


class Update(Common):
    def __init__(self, device, *args):
        super(Update, self).__init__()
        self._log_filename = device
        self._sn = device
        if not os.path.exists(os.environ.get("LOG_PATH") + '\\' + self._sn):
            os.makedirs(os.environ.get("LOG_PATH") + '\\' + self._sn)
        self._logger = logger.Logger(self._log_filename, self._sn + '\\' + self._log_filename + '.log').Logger
        self._device = Device(device)
        self._data = args
        self._settings_pkg, self._settings_act = tuple(x[1] for x in self.get_settings())
        self._update_pkg, self._update_act = tuple(x[1] for x in self.get_update())
        self._ssid, self._pwd = tuple(x[1] for x in self.get_wifi())
        self._ssid1, self._pwd1 = tuple(x[1] for x in self.get_wifi())
        self._old_version, self._new_version = tuple(x[1] for x in self.get_version())
        self._wifi, self._pwd = tuple(x[1] for x in self.get_wifi())
        self._fota_apk, self._push_path, self._upgrade_name = tuple(x[1] for x in self.get_offline())
        self._method = self.get_update_method()
        self._source = self.get_source()

    def remove_device(self):
        cfg = ConfigParser()
        cfg.read(sys.path[0] + '\\config\\devices.ini')
        cfg.remove_option("Devices", self._sn)
        with open(sys.path[0] + '\\config\\devices.ini', 'wb') as fp:
            cfg.write(fp)

    def save_result(self):
        self._logger.debug("save results.")
        line = ''
        with open(os.environ.get('DATA_PATH') + os.sep + self._sn + '.csv', 'a+') as f:
            if self._data[0] == 1:
                f.write(",Loop,device,FlashStartTime,FlashEndTime,PowerOnTime,"
                        "DownloadStartTime,DownloadEndTime,UpdateStartTime,UpdateEndTime,Result\n")
            for index in range(len(self._data)):
                data = self._data[index]
                if isinstance(data, tuple):
                    for d in data:
                        if index >= 2 and (isinstance(d, int) or isinstance(d, float)) and d > 0:
                            d = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(d))
                        line = line + ',' + str(d)
                else:
                    if index >= 2 and (isinstance(data, int) or isinstance(data, float)) and d > 0:
                        data = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(data))
                    line = line + ',' + str(data)
            f.write(line + '\n')

    def try_connect_device(self):
        for loop in range(5):
            try:
                self._logger.debug("Try connect device %s times" % (loop + 1))
                if self.connect_device():
                    return True
            except Exception as e:
                self.save_img()
                self._logger.error(traceback.format_exc())
        self._device.screen.on()

    def connect_device(self):
        if "offline" in self.adb_dos('get-state'):
            self.adb_dos("reconnect offline")
        p = subprocess.Popen(self._device.info, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(120):
            if p.poll() is not None:
                self._logger.debug(self._device.info)
                return True
            time.sleep(1)
        else:
            p.kill()
            self.adb_dos("uninstall com.github.uiautoamtor")
            self.adb_dos("uninstall com.github.uiautoamtor.test")

    def update_system(self):
        try:
            self._logger.debug("*" * 32)
            self._logger.debug(self._data)
            self.try_connect_device()
            for _ in range(5):
                # -- Guangtao
                # 根据当前项目setup wizard包名进行修改
                if self._device.get_current_packagename() == 'com.google.android.setupwizard':
                    self.skip_setup_wizard()
                # memory life time保留：项目在跑了多次后，有可能会出现该界面弹框
                elif self._device(text='memory life time').exists:
                    self._device.press.back()
                else:
                    self._logger.debug("Setup wizard has been skipped.")
                    break
            else:
                self._logger.debug("Skip setup wizard Fail.")
                self.save_img()
                return False
            self.set_never_sleep()
            self.back_to_home()
            if self.try_connect_wifi(self._ssid, self._pwd):
                self.get_wizard_value()
                if self._method == "offline":
                    self.enter_settings('Network & internet', 'Wi-Fi')
                    self.close_wifi()
                    download_time = self.download_zip_offline()
                else:
                    # -- Guangtao
                    # 这里无需第二次切换wifi，故注释掉
                    # self.try_connect_wifi(self._ssid1, self._pwd1)
                    download_time = self.download_zip_online()
                if 0 not in download_time:
                    if self._method == "offline":
                        update_time = self.wait_update_offline()
                    else:
                        update_time = self.wait_update_online()
                    self.get_wizard_value()
                    if 0 not in update_time:
                        result = self.check_update()
                        if result == 'Setup_Wizard':
                            self._data = self._data + ('Fail,Setup Wizard',)
                        elif result is True:
                            self._data = self._data + ('Pass',)
                        else:
                            self._data = self._data + ('Fail,updated version Fail',)
            else:
                self._data = self._data + (',,,,Fail,Connect Wifi Fail',)
        except Exception as e:
            self._logger.error(traceback.format_exc())
        finally:
            if 'offline' in self.adb_dos('get-state').strip():
                self._data = self._data + ('device offline',)
            self.save_result()

    def get_wizard_value(self):
        user_setup_complete = self.adb_dos('shell settings get secure user_setup_complete').strip()
        self._logger.debug("user_setup_complete: %s " % user_setup_complete)
        device_provisioned = self.adb_dos('shell settings get global device_provisioned').strip()
        self._logger.debug("device_provisioned: %s " % device_provisioned)

    # -- Guangtao
    # 根据项目setting菜单下的wifi入口来修改
    def enter_settings(self, option, suboption):
        self._logger.debug('enter settings')
        self._device.start_activity(self._settings_pkg, self._settings_act)
        self._device.delay(2)
        self._logger.debug("enter " + option + " setting")
        if self._device(scrollable=True).exists:
            self._device(scrollable=True).scroll.to(text=option)
        self._device(text=option).click()
        self._device.delay(1)
        self._device(text=suboption).click()
        self._device.delay(1)
        return True

    def reboot_to_edl(self):
        self._device.shell_adb('reboot edl')

    # -- Guangtao
    # 根据项目setup wizard的情况来修改需要跳过的界面、按钮
    def skip_setup_wizard(self):
        steps = ['START', 'Skip', 'Set up offline', 'CONTINUE', 'Next', 'More', 'More', 'Accept', 'Skip', 'Skip',
                 'SKIP ANYWAY', 'Skip', 'Next', 'Next', 'Next', 'Finish', 'SKIP', 'FINISH']
        self._logger.debug("Skip setup wizard.")
        self._device.screen.on()
        try:
            for step in steps:
                if self._device(text='memory life time').exists:
                    self._device.press.back()
                if self._device(text=step).exists:
                    self._device(text=step).click()
                    self._device.delay(2)
            for _ in range(3):
                # -- Guangtao
                # 根据项目launcher包名修改
                # 这里进行判断，当跳过设置向导后，如果在launcher界面，则return True，即当前跳过设置向导成功
                if self._device.get_current_packagename() == "com.tcl.android.launcher":
                    return True
                else:
                    self._device.delay(2)
        except Exception as e:
            self.save_img()
            self._logger.error(traceback.format_exc())

    # -- Guangtao
    # 这里setting菜单下设置休眠时间为never，根据项目情况进行UI修改
    def set_never_sleep(self):
        try:
            self._logger.debug("Set screen timeout: Never")
            self._device.screen.on()
            if self.enter_settings('Display', 'Sleep'):
                # self._device(text='Screen timeout').click()
                # self._device.delay(2)
                self._device(text='Never').click()
                self._device.delay(2)
                return True
            # if self._device(text='Screen timeout').exists:
            #     if self._device(text='Screen timeout').down(text='Never').exists:
            #         return True
        except Exception as e:
            self.save_img()
            self._logger.error(traceback.format_exc())

    def download_zip_offline(self):
        start_time = time.time()
        self._logger.debug("Push %s to sdcard, start time:%s " % (self._upgrade_name, start_time))
        self.adb_dos("push %s %s" % (self._source + self._upgrade_name, self._push_path))
        end_time = time.time()
        data = self.adb_dos("ls %s" % os.path.dirname(self._push_path))
        self._logger.debug("Check upgrade.zip\n" + data)
        if 'upgrade.zip' in data:
            self._logger.debug("Push %s to sdcard, end time:%s " % (self._upgrade_name, end_time))
        else:
            end_time = 0
            self._logger.debug("Can't find upgrade.zip")
        self._data = self._data + (start_time, end_time)
        return start_time, end_time

    def wait_update_offline(self):
        start_time = 0
        end_time = 0
        try:
            self.adb_dos("install -r -g %s" % self._source + self._fota_apk)
            self._device.start_activity("com.android.jrdfotaautotest", "com.android.jrdfotaautotest.FotaMngActivity")
            self._device.delay(5)
            start_time = time.time()
            self._logger.debug("Start update time:%s" % start_time)
            for _ in range(3):
                if self._device(text='memory life time').exists:
                    self._device.press.back()
                if self._device(text='START(0)').exists:
                    self._device(text='START(0)').click()
                    break
            else:
                self._logger.debug("Click start Fail")
                self.save_img()
                return False
            self._logger.debug("%s wait reboot" % self._sn)
            if not self.wait_for_disconnect():
                return False
            old_minute = 0
            self._logger.debug("%s wait power on." % self._sn)
            update_timeout = self.get_update_timeout()
            if not self.wait_for_device():
                return False
            while time.time() - start_time < update_timeout:
                if self.check_launcher_task():
                    self._logger.debug("Update end time:%s" % time.time())
                    end_time = time.time()
                    break
                new_minute = (time.time() - start_time) // 60
                if new_minute > old_minute:
                    old_minute = new_minute
                    self._logger.debug('Wait updating %s minutes' % old_minute)
                time.sleep(1)
            else:
                self._logger.debug("Wait updating timeout (>%ss)" % update_timeout)
                self.save_img()
                self.remove_device()
                self.pull_bugreport()
        except Exception as e:
            self.save_img()
            self._logger.error(traceback.format_exc())
        finally:
            self._data = self._data + (start_time, end_time)
            return start_time, end_time

    def download_zip_online(self):
        start_time = 0
        end_time = 0
        download_timeout = self.get_download_timeout()
        try:
            self._device.start_activity(self._update_pkg, self._update_act)
            self._device.delay(2)
            # -- Guangtao
            # 根据项目情况修改Fota界面当前版本号当控件ID
            old_version = self._device(resourceId='com.tcl.fota.system:id/firmware_current_version').get_text()
            self._logger.debug("Old version:%s" % old_version)
            self._logger.debug("Start download zip time:%s" % time.time())
            start_time = time.time()
            try:
                # 根据项目情况修改 检查升级 按钮的控件信息text
                if self._device(text='CHECK FOR UPDATES').wait.exists(timeout=2000):
                    self._device(text='CHECK FOR UPDATES').click()
            except Exception as e:
                self._logger.warning(traceback.format_exc())
            used_time = 0
            check_for_updates_times = 0
            while True:
                try:
                    # 根据项目情况修改 检查升级 按钮的控件信息text
                    if self._device(text='CHECK FOR UPDATES').wait.exists(timeout=1000):
                        self._device(text='CHECK FOR UPDATES').click()
                        check_for_updates_times += 1
                        if check_for_updates_times // 10 == 9:
                            self._device.shell_adb('shell am force-stop %s' % self._update_pkg)
                            self._device.delay(5)
                            self._device.start_activity(self._update_pkg, self._update_act)
                            self._device.delay(5)
                        if check_for_updates_times > 100:
                            self._logger.debug("Can't get new version.")
                            self.save_img()
                            break
                    # 根据项目情况修改 检查升级 按钮的控件信息text
                    elif self._device(text='INSTALL NOW').wait.exists(timeout=1000):
                        self._logger.debug("Download end time:%s." % time.time())
                        end_time = time.time()
                        break
                    # 根据项目情况修改 检查升级 按钮的控件信息text
                    elif self._device(text='TRY AGAIN').wait.exists(timeout=1000):
                        self._device(text='TRY AGAIN').click()
                        self._logger.debug("TRY AGAIN.")
                        self._device.delay(1)
                        continue
                    # 根据项目情况修改 检查升级 按钮的控件信息text
                    elif self._device(text='PAUSED').wait.exists(timeout=1000):
                        self._device(text='PAUSED').click()
                        self._logger.debug("PAUSE Download.")
                        self._device.delay(1)
                        continue
                    # 根据项目情况修改 检查升级 按钮的控件信息text
                    elif self._device(text='Can\'t use system update').wait.exists(timeout=1000):
                        self._logger.debug("Can't use system update")
                        self.save_img()
                        self.remove_device()
                        return False
                except Exception as e:
                    self._logger.warning(traceback.format_exc())
                    continue
                if time.time() - start_time > download_timeout:
                    self._logger.debug("Download update zip timeout(>30min)")
                    break
                new_minute = (time.time() - start_time) // 60
                if new_minute > used_time:
                    used_time = new_minute
                    self._logger.debug('Wait downloading %s minutes' % used_time)
        except Exception as e:
            self.save_img()
            self._logger.error(traceback.format_exc())
        finally:
            self._data = self._data + (start_time, end_time)
            return start_time, end_time

    def pull_bugreport(self):
        self._logger.debug("pull bugreport")
        self.adb_dos('wait-for-device')
        self.adb_dos('bugreport %s' % (os.environ.get("LOG_PATH") + '\\' + self._sn))
        return True

    def restart_adb(self):
        os.system('adb kill-server && adb start-server')

    def adb_dos(self, commond):
        data = subprocess.Popen('adb -s %s %s' % (self._sn, commond), shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE).communicate()[0]
        return data

    def wait_update_online(self):
        start_time = 0
        end_time = 0
        try:
            # -- Guangtao
            # 根据项目情况修改 检查升级 按钮的控件信息text
            self._device(text='INSTALL NOW').click()
            start_time = time.time()
            self._logger.debug("Start update time:%s" % start_time)
            # self._device(text='INSTALL').click()
            self._logger.debug("%s wait reboot" % self._sn)
            while True:
                if not self.check_launcher_task():
                    break
                if time.time() - start_time > 300:
                    self._logger.error("Install update FAIL!!!")
                    break
            old_minute = 0
            self._logger.debug("%s wait power on." % self._sn)
            update_timeout = self.get_update_timeout()
            while True:
                if self.check_launcher_task():
                    self._logger.debug("Update end time:%s" % time.time())
                    end_time = time.time()
                    break
                new_minute = (time.time() - start_time) // 60
                if new_minute > old_minute:
                    old_minute = new_minute
                    self._logger.debug('Wait updating %s minutes' % old_minute)
                time.sleep(1)
                if time.time() - start_time > update_timeout:
                    self._logger.debug("Wait updating timeout (>%ss)" % update_timeout)
                    self.save_img()
                    self.remove_device()
                    self.pull_bugreport()
                    break
        except Exception as e:
            self.save_img()
            self._logger.error(traceback.format_exc())
        finally:
            self._data = self._data + (start_time, end_time)
            return start_time, end_time

    def check_launcher_task(self):
        var = subprocess.Popen('adb devices', stdout=subprocess.PIPE).communicate()[0]
        for line in var.split('\n'):
            if self._sn in line:
                # -- Guangtao
                # 根据项目情况修改launcher包名
                a = subprocess.Popen('adb -s %s shell "ps -A|grep com.tcl.android.launcher"' % self._sn,
                                     stdout=subprocess.PIPE).communicate()[0]
                return a

    def wait_for_device(self, timeout=600):
        self._logger.debug('wait for device')
        start_time = time.time()
        p = subprocess.Popen('adb -s %s wait-for-device' % self._sn, shell=True, stdout=subprocess.PIPE)
        while time.time() - start_time < timeout:
            if p.poll() is not None:
                return True
            time.sleep(10)
        self._logger.debug('wait for device timeout:%ss' % timeout)

    def wait_for_disconnect(self, timeout=600):
        self._logger.debug('wait for disconnect')
        start_time = time.time()
        p = subprocess.Popen('adb -s %s wait-for-disconnect' % self._sn, shell=True, stdout=subprocess.PIPE)
        while time.time() - start_time < timeout:
            if p.poll() is not None:
                return True
            time.sleep(10)
        self._logger.debug('wait for disconnect timeout:%ss' % timeout)

    def check_update(self):
        fingerprint = self.adb_dos('shell "getprop |grep ro.build.fingerprint').strip()
        self._logger.debug(fingerprint)
        self._logger.debug(self._new_version)
        for version in self._new_version.split(','):
            if version in fingerprint:
                self._logger.debug("Update success.")
                break
        else:
            self._logger.debug("Update Fail.")
            self.save_img()
            self.remove_device()
            self.pull_bugreport()
            return False
        self.adb_dos("uninstall com.android.jrdfotaautotest")
        self._device.screen.on()
        self._device.delay(1)
        for _ in range(6):
            current_pkg = self._device.get_current_packagename()
            if current_pkg:
                # -- Guangtao
                # 根据项目情况修改setup wizard包名
                if 'com.google.android.setupwizard' in current_pkg:
                    self._logger.error("open setup wizard, after update.")
                    self.save_img()
                    self.remove_device()
                    self.pull_bugreport()
                    return "Setup_Wizard"
                else:
                    self._logger.debug("Update Pass.")
                    return True
            else:
                self._device.delay(10)

    def save_img(self, newimg=None):
        dir_path = os.sep.join([os.environ.get('LOG_PATH'), self._sn, "Error_pic"])
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        path = os.sep.join([dir_path, datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + ".png"])
        if newimg is None:
            self._logger.debug("Take snapshot.")
            self._logger.error("Fail: %s" % path)
            self._device.screenshot(path)
        return True

    def try_connect_wifi(self, hotspot_name, password):
        for loop in range(5):
            try:
                # -- Guangtao
                # 使用命令启动wifi
                self.adb_dos("svc wifi enable")
                self._device.delay(15)
                if self.connect_wifi(hotspot_name, password):
                    return True
                else:
                    self._logger.debug("Try connect %s times" % (loop + 1))
                    self.close_wifi()
                    self._device.delay(10)
                    if loop >= 4:
                        self._logger.debug("Try connect %s times failed" % (loop + 1))
                        self.save_img()
                        break
            except Exception as e:
                self.save_img()
                self._logger.debug(traceback.format_exc())
            finally:
                self.back_to_home()
        if self.get_update_method().lower() == "offline":
            return True

    # -- Guangtao
    # 无实际效用，故注释掉
    # def open_wifi(self):
    #     self._logger.debug("Open wifi")
    #     if self._device(className='android.widget.Switch', checked=False).exists:
    #         self._device(className='android.widget.Switch', checked=False).click()
    #         self._device.delay(2)
    #     if self._device(className='android.widget.Switch', checked=True).exists:
    #         self._logger.debug("Open wifi success")
    #         return True

    def close_wifi(self):
        self._logger.debug("close wifi")
        self.adb_dos('svc wifi disable')
        return True

    # -- Guangtao
    # 根据项目情况修改UI路径
    def connect_wifi(self, hotspot_name=None, password=None):
        if hotspot_name is None:
            hotspot_name = self._wifi
        if password is None:
            password = self._pwd
        self.enter_settings('Network & internet', 'Wi-Fi')
        self._logger.debug('Search hotspot-------> ' + hotspot_name)
        self._device.delay(10)
        self._device(scrollable=True).scroll.vert.toBeginning(steps=30, max_swipes=10)
        for _ in range(10):
            if self._device(text=hotspot_name).exists:
                self._device(text=hotspot_name).click()
                self._device.delay(2)
                break
            else:
                self._device(scrollable=True).scroll.vert.forward(steps=30)
            self._device.delay(1)
        # 根据实际UI控件情况修改
        if self._device(text='Password').exists:
            self._logger.debug('input password-------> ' + password)
            self._device(className='android.widget.EditText').click()
            self._device.delay(1)
            self._device.shell_adb("shell input text %s" % password)
            self._device.delay(2)
            self._device(text="CONNECT").click()
            if self._device(textContains="Connected").wait.exists(timeout=20000):
                self._logger.debug('wifi connect success!!!')
                return True
        self._logger.debug('wifi connect fail!!!')
        return False

    def back_to_home(self):
        self._logger.debug("back to home page.")
        maxloop = 0
        # -- Guangtao
        # 根据实际项目launcher主界面显示情况修改控件resourceId
        while not self._device(resourceId="com.tcl.android.launcher:id/layout").exists:
            self._device.press.back()
            self._device.press.home()
            self._device.delay(2)
            if maxloop > 6:
                self._device.press.home()
                self._device.delay(2)
                break
            maxloop += 1
        if self._device(resourceId="com.tcl.android.launcher:id/layout").exists:
            self._device.press.home()
            return True
        self._logger.debug("back to home page fail.")
        return False

    def offline_update(self):
        self._logger.debug(self.get_offline())
        self.adb_dos("push %s %s" % (self._source + self._upgrade_name, self._push_path))
        self.adb_dos("install -r -g %s" % self._source + self._fota_apk)
        self.adb_dos("reboot")
        time.sleep(10)
        self.adb_dos("wait-for-device")
        time.sleep(10)
        self.adb_dos("shell am start -n com.android.jrdfotaautotest/com.android.jrdfotaautotest.FotaMngActivity")
        time.sleep(10)
        self.adb_dos("shell input tap 100 680")


if __name__ == "__main__":
    u = Update('a0d0c6bc', 1, 'a0d0c6bc', 22222, 33333, 44444, 55555)
    # u.wait_for_device()
    # u.download_zip_offline()
    # u.check_update()
    u.update_system()
    # u.try_connect_device()
    # u.connect_wifi('HH71V1_803C_5G', 'jitlitli')
    # a =u.find_launcher()
    # if a:
    #     print (a)
    # u.check_update()
    # u.connect_wifi()
    # u.pull_bugreport()
