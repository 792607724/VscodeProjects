# coding = utf8

import subprocess
import multiprocessing
from time import sleep

appcrawer_jar = "/Users/cgt/Downloads/appcrawler-2.4.0-jar-with-dependencies.jar"
# apk_path = "/Users/cgt/Downloads/TctSettings.apk"
# apk_path = "/Users/cgt/Downloads/TctGallery.apk"
apk_path = "/Users/cgt/Downloads/Chrome.apk"
package_name = "com.android.settings"
config_yaml = "/Users/cgt/VscodeProjects/demo.yml"


def launch_appium():
    cmd = "appium --session-override"
    adb_dos(cmd)

    """NOT_FOUND ELEMENT_NOT_FOUND xpath=/* (AutomationSuite.scala:45)
    """

def launch_test():
    cmd = "java -jar {} -a {}".format(appcrawer_jar, apk_path)
    # cmd = "java -jar {} -c {}".format(appcrawer_jar, config_yaml)
    adb_dos(cmd)

def adb_dos(cmd):
    result = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    while True:
        line = result.stdout.readline()
        print(line.decode("utf-8"))
        if line == b"" or subprocess.Popen.poll(result) == 0:
            result.stdout.close()
            break

def create_Process_pool():
    test_pool = multiprocessing.Pool(2)
    test_pool.apply_async(func=launch_appium, args=())
    sleep(5)
    test_pool.apply_async(func=launch_test, args=())
    test_pool.close()
    test_pool.join()

create_Process_pool()


