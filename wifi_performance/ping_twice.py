# coding = utf8

import uiautomator2 as u2
from time import sleep
import os

d = u2.connect("b3e5b958")

d.app_start("jackpal.androidterm")

cmd1 = "ping -c 2 www.baidu.com>/storage/emulated/0/ping1.txt"
frame = d(resourceId="jackpal.androidterm:id/view_flipper").child()
frame.click()
d.set_fastinput_ime(True) # 切换成FastInputIME输入法
d.send_keys(cmd1) # adb广播输入
d.set_fastinput_ime(False) # 切换成正常的输入法
d.press("enter")

# sleep(6 * 60 * 60)
sleep(5)

cmd2 = "ping -c 2 www.baidu.com>/storage/emulated/0/ping2.txt"
d.set_fastinput_ime(True) # 切换成FastInputIME输入法
d.send_keys(cmd2) # adb广播输入
d.set_fastinput_ime(False) # 切换成正常的输入法
d.press("enter")



