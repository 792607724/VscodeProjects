# coding = utf8

import os
os.path.abspath(".")
import threading
import multiprocessing

"""Python provided 2 module for thread function:_thread and threading
at most situation we use threading the advanced module

Multithreading in python is a complex module, we need use lock to diveded them and prevent
dead lock in the meantime
By the way, python have a GIL lock, its occurs multithread cannot use multi core.
But we can use multiprocess combine with multithread to accompulish it.
"""

def print_temp(label = "Yes"):
    print("I'm a case for debugging! %s " % label)

def create_thread():
    # 任何进程默认都会启动一个线程，该线程叫主线程
    # 创建一个线程，并指定线程中运行的方法，指定线程名称为Subthread
    print("This process's main thread is %s" % threading.current_thread().name)
    t = threading.Thread(target = print_temp, args = ("No",), name = "Subthread")
    t.start()
    t.join()
    print("Thread %s ended" %threading.current_thread().name)

######################################################################
balance = 0
def change_balance(n):
    global balance # 外面定义了共享变量，函数内需要获取，需要用到global声明
    balance += n
    balance -= n

lock = threading.Lock()
def run_thread(n):
    for i in range(1000):
        lock.acquire()  # 先获取锁
        try:
            change_balance(n)   # 线程开始操作
        finally:
            lock.release()  # 释放锁给下一个线程

def lock_thread():
    thread_1 = threading.Thread(target = run_thread, args = (10,), name = "Thread_1")
    thread_2 = threading.Thread(target = run_thread, args = (90,), name = "Thread_2")
    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()
    print(balance)
######################################################################

def loop_case():
    #这里写一个死循环看线程执行后CPU占用情况
    x = 0
    while True:
        x *= 1

def death_thread():
    """但是用C、C++或Java来改写相同的死循环，直接可以把全部核心跑满，4核就跑到400%，8核就跑到800%，
    为什么Python不行呢？
    因为Python的线程虽然是真正的线程，但解释器执行代码时，有一个GIL锁：Global Interpreter Lock，
    任何Python线程执行前，必须先获得GIL锁，然后，每执行100条字节码，解释器就自动释放GIL锁，让别的线程有机会执行。
    这个GIL全局锁实际上把所有线程的执行代码都给上了锁，所以，多线程在Python中只能交替执行，
    即使100个线程跑在100核CPU上，也只能用到1个核
    """
    for i in range(multiprocessing.cpu_count()):
        t = threading.Thread(target = loop_case, args = ())
        t.start()
    # Python虽然不能利用多线程实现多核任务，但可以通过多进程实现多核任务。多个Python进程有各自独立的GIL锁，互不影响。

if __name__ == "__main__":
    # death_thread()
    pass