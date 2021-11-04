# coding=utf-8
import os
import re
import subprocess
import sys
import time
import traceback

import cv2
import serial.tools.list_ports as lp
import uiautomation as auto

import logger
from common import Common


class Flash(Common):
    def __init__(self, port, log_name="Flash"):
        super(Flash, self).__init__()
        self._logger = logger.Logger(log_name).Logger
        self._port = port
        self._tclbin = self.get_tclbin()
        self._tpst = r'{7C5A40EF-A0FB-4BFC-874A-C0F2E0B9FA8E}\TCT\TPST\Tool\TPST.exe'
        self._tpst_path = self.get_tpst()

    # -- Guangtao
    # 无实际效用，故注释掉
    # def restart_adb(self):
    #     os.system('adb kill-server && adb start-server')

    def check_port_9008_exists(self, wait_time=300):
        self._logger.debug("Check port:%s exists?" % self._port)
        for _ in range(wait_time):
            port_list = lp.comports()
            is_break = False
            for port in port_list:
                if self._port in port.description:
                    is_break = True
            if is_break:
                return True
            time.sleep(1)
        self._logger.warning("Check port:%s timeout" % self._port)

    def get_9008_port(self):
        port_list = []
        ports = lp.comports()
        for port in ports:
            if self._port in port.description:
                if port.description not in port_list:
                    port_list.append(port.description)
        return port_list

    def try_open_qpst(self, try_time=3):
        for loop in range(try_time):
            self._logger.debug("Try open qpst %s times" % (loop + 1))
            if self.open_qpst():
                return True
        else:
            self._logger.debug("open qpst failed.")

    def open_qpst(self, tclbin=None):
        try:
            self._logger.debug("Load TPST")
            subprocess.Popen(r'taskkill /F /IM TPST.exe').wait()
            time.sleep(5)
            subprocess.Popen(self._tpst_path)
            time.sleep(10)
            # -- Guangtao
            # 这边需要修改Page的名称T781.jpg
            for jpg in ["Load.jpg", "T781.jpg", "Button_OK.jpg", "Refurbish.jpg", "Browse1.jpg", "Path.jpg"]:
                if auto.GetFocusedControl().ClassName != 'Qt5QWindowIcon':
                    return False
                if jpg == 'Button_OK.jpg':
                    self.click_image(jpg)
                else:
                    if not self.click_image(jpg):
                        return False
            TPST = auto.GetFocusedControl()
            TPST.SendKeys('{Ctrl}{a}')
            if tclbin is None:
                self._logger.debug("Guangtao -- tclbin is None" + str(self._tclbin))
                tclbin = self._tclbin
            else:
                self._logger.debug("Guangtao -- tclbin is not None" + str(self._tclbin))
                tclbin = self._abl
            TPST.SendKeys(tclbin)
            TPST.SendKeys('{Enter}')
            return True
        except Exception as e:
            self._logger.debug(traceback.format_exc())

    def refurbish(self):
        for _ in range(3):
            try:
                self._logger.debug("Open TPST, and start refurbish.")
                root = auto.GetRootControl()
                if auto.GetFocusedControl().ClassName != 'Qt5QWindowIcon':
                    masklist = root.ToolBarControl()
                    tpst_icon = masklist.ButtonControl(searchDepth=1, AutomationId=self._tpst)
                    if tpst_icon:
                        tpst_icon.Click()
                        time.sleep(2)
                    else:
                        self._logger.warning("Can't find TPST icon in mask list.")
                        return False
                focused_control = auto.GetFocusedControl().ClassName
                self._logger.debug(auto.GetFocusedControl().ClassName)
                if focused_control != 'Qt5QWindowIcon':
                    self._logger.warning("Open QPST FAILED.")
                    return False
                if self.click_image('start_refurbish.jpg'):
                    start_time = time.time()
                    self._logger.debug("Start flash time:%s" % start_time)
                    return start_time
                else:
                    self._logger.debug("Can't get TPST 'Start Refurbish' button.")
            except Exception as e:
                self._logger.warning(traceback.format_exc())

    def get_devices(self):
        data = subprocess.Popen('adb devices', stdout=subprocess.PIPE).communicate()[0]
        devices = []
        pattern = r'(\w+)(\s+)(device)'
        for line in data.split('\n'):
            if 'devices' in line:
                continue
            r1 = re.search(pattern, line)
            if r1:
                d = r1.groups()[0]
                if d not in devices:
                    devices.append(d)
        return devices

    def shell_dos(self, device, command):
        data = subprocess.Popen('adb -s %s %s' % (device, command), stdout=subprocess.PIPE).communicate()[0]
        return data

    def reboot_edl(self, device):
        if "offline" in self.shell_dos(device, 'get-state'):
            self.shell_dos(device, "reconnect offline")
        return self.shell_dos(device, 'reboot edl')

    # -- Guangtao
    # 根据项目setup wizard包名不同进行修改
    def wait_power_on(self, device):
        data = self.shell_dos(device, 'shell "ps -A|grep com.google.android.setupwizard"')
        if data:
            return data
        # 根据launcher名称进行修改
        launcher = self.shell_dos(device, 'shell "ps -A|grep launcher"')
        if launcher:
            return launcher

    def wait_all_device_power_on(self, devices=[]):
        power_on_time = {}
        self._logger.debug('Wait  power on time:%s.' % time.time())
        if len(devices) == 0:
            self._logger.debug("Can't find any device.")
            return False
        for device in devices:
            power_on_time[device] = 0
        for _ in range(600):
            current_devices = self.get_devices()
            for device in current_devices:
                if device in devices:
                    if self.wait_power_on(device):
                        power_on_time[device] = time.time()
                        self._logger.debug("%s power on end time: %s" % (device, time.time()))
                        devices.remove(device)
            if not devices:
                break
            time.sleep(1)
        self._logger.debug("All devices on online")
        time.sleep(15)
        return power_on_time

    def wait_for_device(self, device):
        self._logger.debug('wait for device:%s' % device)
        return self.shell_dos(device, 'wait-for-device')

    # -- Guangtao
    # 无实际效用，故注释掉
    # def wait_recovery_power_on(self):
    #     self._logger.debug("wait recovery update 5 minutes")
    #     time.sleep(300)

    def wait_all_devices(self, devices):
        self._logger.debug('wait 5 minutes for all device back online.')
        for _ in range(300):
            flag = True
            for device in devices:
                if self.wait_for_device(device):
                    self._logger.debug("%s back on online" % device)
                    flag = flag & True
                else:
                    flag = flag & False
                time.sleep(1)
            if flag is True:
                self._logger.debug("All devices back on online")
                time.sleep(10)
                return True

    def click_image(self, pic_name):
        try:
            location = self.find_image(pic_name)
            time.sleep(2)
            if location:
                self._logger.debug("click (%s %s)" % location)
                root = auto.GetRootControl()
                root.Click(location[0], location[1])
                return True
        except Exception as e:
            self._logger.error(traceback.format_exc())

    def find_image(self, pic_name, threshold=0.001, rotation=0, save_img=True):
        try:
            cur_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            screenshot_path = os.sep.join([sys.path[0], 'tmp', 'screenshot_%s.bmp' % cur_time])
            self.screenshot_desk(screenshot_path)
            compare_pic = os.sep.join([sys.path[0], "picCompare", pic_name])
            location = self.get_matched_center_offset(compare_pic, screenshot_path, threshold=threshold,
                                                      rotation=rotation)
            time.sleep(2)
            if location:
                self._logger.debug("Find image:%s" % pic_name)
                if save_img:
                    os.remove(screenshot_path)
                return location
            else:
                self._logger.debug("Can't find image:%s" % pic_name)
        except Exception as e:
            self._logger.error(traceback.format_exc())

    def adapt_rotation(self, coord, size, rotation=0):
        if rotation == 0:
            return coord
        elif rotation == 90:
            height, width = size
            x_coord, y_coord = coord
            x = y_coord
            y = width - x_coord
            return x, y
        elif rotation == 180:
            height, width = size
            x_coord, y_coord = coord
            x = x_coord
            y = y_coord
            return x, y
        elif rotation == 270:
            height, width = size
            x_coord, y_coord = coord
            x = height - y_coord
            y = x_coord
            return x, y
        else:
            return None

    def get_matched_center_offset(self, sub_path, src_path, threshold=0.03, rotation=0):
        """
        匹配图片，若成功则返回匹配位置的中心坐标，否则返回None
        :param sub_path: 需要匹配的图片。
        :param src_path: 当前位置的图片。
        :param threshold:
        :param rotation:
        :return:
        """
        for img in [sub_path, src_path]:
            assert os.path.exists(img), "No such image:  %s" % img
        method = cv2.cv.CV_TM_SQDIFF_NORMED
        try:
            sub_img = cv2.imread(sub_path)
            src_img = cv2.imread(src_path)
            result = cv2.matchTemplate(sub_img, src_img, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if min_val <= threshold:
                min_loc_x_point, min_loc_y_point = min_loc
                sub_img_column, sub_img_row = sub_img.shape[:2]
                center_point = (min_loc_x_point + int(sub_img_row / 2), min_loc_y_point + int(sub_img_column / 2))
                # if image is binary format shape return (w, h) else return (w, h, d)
                (height, width) = src_img.shape[:2]
                return self.adapt_rotation(coord=center_point, size=(height, width), rotation=rotation)
            else:
                return None
        except Exception as e:
            return None

    def screenshot_desk(self, file_path):
        bitmap = auto.Bitmap()
        bitmap.FromHandle(0)
        if not os.path.exists(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))
        bitmap.ToFile(file_path)
        if file_path:
            return file_path

    def wait_refurbish(self):
        """
        判断9008端口是否消失，
        若消失则返回当时的时间。
        若超时则返回0
        :return:
        """
        self._logger.debug("Wait about 3~5 min for flashing_img image.")
        end_time = 0
        try:
            for _ in range(900):
                port_list = lp.comports()
                is_break = True
                for port in port_list:
                    if self._port in port.description:
                        is_break = False
                if is_break:
                    self._logger.debug("Flash end time:%s" % time.time())
                    end_time = time.time()
                    break
                time.sleep(1)
            else:
                self._logger.warning("refurbish [%s] timeout" % self._port)
        except Exception as e:
            self._logger.error(traceback.format_exc())
        finally:
            return end_time

    def flashing_img(self):
        start_time, end_time = 0, 0
        try:
            if self.check_port_9008_exists():
                start_time = self.refurbish()
                if start_time:
                    end_time = self.wait_refurbish()
        except Exception as e:
            self._logger.error(traceback.format_exc())
        finally:
            return start_time, end_time

    def click_tpst(self):
        """
        click tpst every 4 minutes,In case the screen goes out
        :return:
        """
        while True:
            try:
                if auto.GetFocusedControl().ClassName != "Qt5QWindowIcon":
                    root = auto.GetRootControl()  # get root
                    masklist = root.ToolBarControl()  # get mast list
                    tpst_icon = masklist.ButtonControl(searchDepth=1, AutomationId=self._tpst)  # get TPST icon
                    self._logger.debug("Click %s " % tpst_icon.Name)
                    tpst_icon.Click()  # click TPST icon
                self._logger.debug("Click %s" % auto.GetFocusedControl().ClassName)
                auto.GetFocusedControl().Click(100, 90)
                time.sleep(240)
            except Exception as e:
                self._logger.debug(traceback.format_exc())


if __name__ == "__main__":
    d = Flash('Android HS-USB QDLoader 9008', log_name="DOWNLOAD")
    # d.click_tpst()
    d.open_qpst('abl')
    # port_list = lp.comports()
    # for port in port_list:
    #     print port.description
