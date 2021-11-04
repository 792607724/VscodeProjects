# coding = utf8

import os
os.path.abspath(".")
import random, time, queue
from multiprocessing.managers import BaseManager


# 发送任务队列
task_queue = queue.Queue()
# 接收结果队列
result_queue = queue.Queue()

# 从BaseManager继承的QueueManager
class QueueManager(BaseManager):
    pass

# 把两个Queue注册到网络上，callable参数关联了Queue对象
QueueManager.register("get_task_queue", callable = lambda : task_queue)
QueueManager.register("get_result_queue", callable = lambda : result_queue)

# 绑定端口5000，设置验证码“abc”
manager = QueueManager(address = ("", 5000), authkey = b"abc")

# 启动Queue
manager.start()

# 获得通过网络访问到Queue对象
task = manager.get_task_queue()
result = manager.get_result_queue()

# 放个任务进去
task.put("这是一个任务")
print("Put task in……")

# 从result队列读取结果
print("Try get result from queue")
r =result.get(timeout = 10000)
print("Result is %s" %r)

# 关闭
manager.shutdown()
print("Master exit.")
