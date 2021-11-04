# coding=utf-8
import ConfigParser
import multiprocessing as mp
import os
import sys
import time
import traceback
import ctypes

import lib.common as m_com
import lib.logger
from lib.common import Common
from lib.flash import Flash
from lib.update import Update

m_com.create_folder()
logger = lib.logger.Logger("MAIN").Logger
m_flash = Flash('9008')
devices_dict = {}

ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
ES_AWAYMODE_REQUIRED = 0x00000040
ES_CONTINUOUS = 0x80000000


def set_display_required():
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)


def display_release():
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)


def update_sw(device, loop, sn, flash_time, power_on_time):
    Update(device, loop, sn, flash_time, power_on_time).update_system()


# -- Guangtao
# 无实际效用，故注释掉
# def move_mouse(_time):
#     """
#     为了避免公司电脑锁屏，每240s点击一次TPST
#     :param _time:
#     :return:
#     """
#     m_flash.click_tpst()


def reboot_devices():
    devices = m_flash.get_devices()
    logger.debug(devices)
    for device in list(set(devices) & set(devices_dict.keys())):
        logger.debug("%s reboot edl" % device)
        m_flash.reboot_edl(device)
        time.sleep(10)


def add_devices():
    """
    重启手机，并将sn与port对应
    :return:
    """
    cfg = ConfigParser.ConfigParser()
    cfg.add_section("Devices")
    devices = m_flash.get_devices()
    logger.debug(devices)
    old_port = []
    for device in devices:
        logger.debug("%s reboot edl" % device)
        time.sleep(10)
        m_flash.reboot_edl(device)
        time.sleep(10)
        new_port = m_flash.get_9008_port()
        for port in new_port:
            if port not in old_port:
                cfg.set('Devices', device, port)
        old_port = new_port
    with open(sys.path[0] + '\\config\\devices.ini', 'wb') as fp:
        cfg.write(fp)


def main(loop):
    global devices_dict
    devices_dict = {}
    cfg = ConfigParser.ConfigParser()
    cfg.read(sys.path[0] + '\\config\\devices.ini')
    for k, v in cfg.items('Devices'):
        devices_dict[k] = v
    logger.debug(devices_dict.keys())
    logger.debug(devices_dict.values())

    flag = True
    m_flash.try_open_qpst()
    reboot_devices()
    flash_time = ()
    if flag:
        flash_time = m_flash.flashing_img()
        if 0 in flash_time:
            flag = flag & False

    power_on_time = {}
    if flag:
        power_on_time = m_flash.wait_all_device_power_on(devices_dict.keys())
        if not power_on_time:
            flag = flag & False
    if flag:
        # -- Guangtao
        # 使用进程池创建为每台机器创建进程
        logger.debug("Open process pool:%s" % (len(devices_dict)))
        pool = mp.Pool(len(devices_dict))
        logger.debug(devices_dict.keys())
        for device in devices_dict.keys():
            # 使用apply_async开始进程所需调用的方法，传入参数
            pool.apply_async(update_sw, (device, loop + 1, device, flash_time, power_on_time[device],))
            # 每台机器进程之间创建间隔为120s，防止adb串用
            time.sleep(120)
        pool.close()
        pool.join()


def save_total_result(loop, start_time, end_time):
    with open(os.environ.get("DATA_PATH") + '\\main.csv', 'a+') as f:
        if loop == 1:
            f.write("loop,start_time,end_time\n")
        f.write('%s,%s,%s\n' % (loop,
                                time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(start_time)),
                                time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(end_time))))


if __name__ == "__main__":
    # -- Guangtao
    """
        测试流程：
        1、电脑关掉息屏
            2、开启TPST刷机工具
            3、等待手机连接端口9008
            4、刷机->开机
            5、跳过设置向导->设置Sleep：never->连接wifi->检测升级包->下载、升级
            6、安装->启动到Launcher->第一次升级测试OK
            ->下一轮测试以此循环
        2、一般一台電腦跑4台在綫的，機器太多會很慢，不要用hub口，數據傳輸會很慢
    """
    # 初始化设备
    add_devices()
    # 设置PC屏幕显示常亮
    set_display_required()
    # 获取每台机器循环跑的次数
    times = Common().get_loop()
    # 开始循环main
    for loop in range(times):
        logger.debug("\n" + "*" * 32)
        logger.debug("[Loop-%s] Start time:%s" % (loop + 1, time.time()))
        start_time = time.time()
        try:
            main(loop)
        except Exception as e:
            logger.debug(traceback.format_exc())
        finally:
            logger.debug("[Loop-%s] End time:%s" % (loop + 1, time.time()))
            end_time = time.time()
            # 记录结束时间保存结果
            save_total_result(loop + 1, start_time, end_time)
    # 恢复PC屏幕显示
    display_release()
