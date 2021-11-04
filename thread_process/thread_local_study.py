# coding = utf8

import os
os.path.abspath(".")
import threading

"""In multithread running's environment, each thread have their own data, use partial variable is 
better than global variable, but partial variable deliver is complex, so we use ThreadLocal to
control thread's own variable
"""
"""ThreadLocal最常用的地方就是为每个线程绑定一个数据库连接，HTTP请求，用户身份信息等，
这样一个线程的所有调用到的处理函数都可以非常方便地访问这些资源。

一个ThreadLocal变量虽然是全局变量，但每个线程都只能读写自己线程的独立副本，互不干扰。
ThreadLocal解决了参数在一个线程中各个函数之间互相传递的问题
""" 

# 创建全局ThreadLocal对象
local_school = threading.local()

def process_student():
    std = local_school.student
    print(threading.current_thread().name ,local_school.student)

def process_thread(name):
    local_school.student = name
    process_student()


if __name__ == "__main__":
    thread_1 = threading.Thread(target = process_thread, args = ("Bruce",), name = "Thread_1")
    thread_2 = threading.Thread(target = process_thread, args = ("Alice",), name = "Thread_2")
    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()