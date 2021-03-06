# coding = utf8

import os
os.path.abspath(".")
import time, sys, queue
from multiprocessing.managers import BaseManager

# 创建类似到QueueManager
class QueueManager(BaseManager):
    pass

# 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字
QueueManager.register("get_task_queue")
QueueManager.register("get_result_queue")

# 连接到服务器，运行task_master.py的机器
server_addr = "127.0.0.1"
print("Connect to server %s……" %server_addr)

#端口和验证码注意保持与task_master.py设置的一致：
m = QueueManager(address = (server_addr, 5000), authkey = b"abc")

#从网络连接
m.connect()

# 获取Queue的对象
task = m.get_task_queue()
result = m.get_result_queue()

# 从队列取任务，并把结果写入result队列
try:
    n = task.get(timeout = 1)
    time.sleep(1)
    r = "任务完成"
    result.put(r)
except queue.Empty:
    print("任务队列是空的")
