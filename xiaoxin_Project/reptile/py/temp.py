# coding = utf8

import os
os.path.abspath("")

from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import sys

import logging
logger = logging.getLogger("airtest")
logger.setLevel(logging.INFO)

SERIAL_NUMBER = "7c2440fd"

cur_device = connect_device("Android:///{}".format(SERIAL_NUMBER))
poco = AndroidUiautomationPoco()

home()
logger.error(cur_device.get_top_activity()[0])
class A:

    def __init__(self):
        pass
    
    def getA(self):
        return sys._getframe().f_code.co_name

a = A()
logger.error(a.getA())
logger.info("function:" + sys._getframe().f_code.co_name + ":启动calendar app:")

logger.error("function:" + sys._getframe().f_code.co_name +
                             ":无需进行location授权界面:" + str(ex))

logger.warning("function:" + sys._getframe().f_code.co_name +
                             ":无需进行location授权界面:" + str(ex))                             

# case :
    @allure.description("")
    @allure.step("")
    def test_(self, before_all_case_execute):
        pass
        