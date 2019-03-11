#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : queue_study.py
@Time : 2019/03/08 15:16:08
@Author : zhangtyps
@GitHub : https://github.com/zhangtyps
@Version : 1.0
@Desc : 如何理解threading和queue的配合使用
'''

# here put the import lib
import threading, queue, random, time


class MyThread(threading.Thread):
    def __init__(self, i, queue):
        #类初始化时，带入需要的参数和刚才创建的队列
        threading.Thread.__init__(self)
        self.queue = queue
        self.i = i

    def run(self):
        #当类的实例调用start()时运行的代码
        time.sleep(random.randint(1, 3))
        print('thread %s is over' % self.i)
        #当运行完，调用get()从对列表里找到该任务，task_down通知该线程任务已完成
        self.queue.get()
        self.queue.task_done()


def main():
    #创建一个队列，长度最大为3
    q = queue.Queue(3)
    #往队列里丢15个任务，虽然超过了队列长度，但是任务执行还是一次只能执行3个
    for i in range(15):
        #把任务添加到队列中，如果添加超过队列长度，将会等待
        #这里put添加的值其实没有任何意义，只是一个在队列里的占位符而已，全部put(1)也不会有任何报错
        q.put(i)
        #实例化类，并运行
        t = MyThread(i, q)
        t.start()
    #这里的q.join()实际上在等待最后队列中的任务，因为put本身就会因为队列长度不够而等待，最好加上这个函数
    q.join()
    print('over')


if __name__ == '__main__':
    main()