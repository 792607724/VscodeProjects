# coding=utf-8

import sys, os
from ConfigParser import ConfigParser
import time

data = time.strftime("%Y%m%d_%H%M%S")


def create_folder():
    data_path = os.environ.get("DATA_PATH")
    if data_path is None:
        data_path = os.path.join(sys.path[0], 'results', data)
        os.environ["DATA_PATH"] = data_path
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    log_path = os.environ.get('LOG_PATH')
    if log_path is None:
        log_path = os.path.join(sys.path[0], 'log', data)
        os.environ['LOG_PATH'] = log_path
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    return data_path, log_path


class Common(object):
    def __init__(self, config=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'common.ini')):
        create_folder()
        self._cfg = ConfigParser()
        self._common = config
        self._cfg.read(self._common)
        self._loop = self._cfg.getint('Default', 'loop')

    def get_source(self):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "source")

    def get_wifi(self):
        return self._cfg.items('Wifi')

    def get_wifi1(self):
        return self._cfg.items('Wifi1')

    def get_settings(self):
        return self._cfg.items('Settings')

    def get_update(self):
        return self._cfg.items('Update')

    def get_version(self):
        return self._cfg.items('Version')

    def get_tclbin(self):
        return self.get_source() + self._cfg.get("Default", 'tclbin')

    # -- Guangtao
    # 无实际效用，故注释掉
    # def get_abl(self):
    #     return self.get_source() + self._cfg.get("Default", 'abl')
    #     # return "./source/" + self._cfg.get("Default", 'abl')

    def get_loop(self):
        return self._cfg.getint('Default', 'loop')

    def get_update_timeout(self):
        return self._cfg.getint('Timeout', 'update')

    def get_download_timeout(self):
        return self._cfg.getint('Timeout', 'download')

    def get_offline(self):
        return self._cfg.items("Offline")

    def get_update_method(self):
        return self._cfg.get('Default', 'update_method')

    def get_tpst(self):
        return self._cfg.get('Default', 'tpst')
