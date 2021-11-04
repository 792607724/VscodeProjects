# coding = utf8

import os
os.path.abspath(".")
from multiprocessing import Process, Pool, Queue
from datetime import datetime
from time import sleep
import random
import subprocess

"""Thread & Process in Python
If a program need execute more than one task, we have three solution:
1.Create more than one process to do them
2.Create one process and its contained several thread
3.Create several process and several thread

Summary:
Thread is the smallest execute unit, and process at least have one thread, and how to adjust process
based on cpu and operate system, program cannot affect it.
Multiprocess and multithread related to syncronized and data sharing, will be more complex
"""

def get_process_pid():
    # 获取子进程和父进程的pid
    print("Process %s start……" % os.getpid())
    print("Process father is %s" % os.getppid())
    pid = os.fork()
    if pid == 0:
        print("I'm child process %s and my father process is %s" % (os.getpid(), os.getppid()))
    else:
        print("I %s just create a child process %s" % (os.getpid(), pid))

def print_temp(label = "Yes"):
    print("I'm a case for debugging! %s " % label)

def print_current_time():
    sleep(random.uniform(0.5, 3.5))
    print(datetime.now().strftime("%Y-%m-%d/%H:%M:%S"))

def create_multiprocessing():
    # 使用multiprocessing创建进程,target:进程中执行的方法，args:进程中执行方法的参数
    process = Process(target = print_temp, args = ("No",))
    print("Process start……")
    process.start()
    process.join()  # join will wait for process execute over then keep running
    print("Process end……")

def create_process_pool():
    p = Pool(9) # 9表示CPU同时运行进程上限数量，即CPU核数
    print("Create 10 process")
    for i in range(10): # 创建10个进程
        p.apply_async(print_current_time, args = ()) # 创建进程并运行
    p.close()   # 先关闭创建进程才能开始join，保证一个完成后执行下一个
    p.join()
    print("All process finished!")

def create_subprocess():
    print("Create a subprocess")
    subprocess.call("python3 --version", shell = True)  # 命令行显示python版本
    subprocess.call("open -a qqmusic", shell = True)    # 命令行启动QQ音乐 -macos
    print("Subprocess work done!")

def subprocess_need_input():
    # 当子进程需要输入时
    p = subprocess.Popen(["python3"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    output, err = p.communicate(b"print('Hello')")  # 将字符串转成byte对象
    print(output.decode("utf-8"))
    print("P.returncode: %s" %(p.returncode))

def communication_between_process():
    # 进程间通讯    创建一个队列，创建两个进程，一个写入，一个读取
    q = Queue()
    pw = Process(target = write, args = (q,))
    pr = Process(target = read, args = (q,))
    pw.start()
    pr.start()
    pw.join()   # 等待写入完成
    pr.terminate()  # read是死循环所以直接终止

def write(q):
    print("Process to write %s", os.getpid())
    for value in ["A", "B", "C"]:
        q.put(value)
        sleep(random.random())

def read(q):
    print("Process to read %s", os.getpid())
    while True:
        value = q.get(True)
        print("Get %s from queue" %value)

if __name__ == "__main__":
    communication_between_process()

