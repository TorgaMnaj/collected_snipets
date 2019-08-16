#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#
#  Copyright 2016 rob <rob@dellix>
#
#
#


import time
import random
import os

# these imports differ between 'threading' and 'multiprocessing' gist
from Queue import Empty
from multiprocessing import Process, Lock, JoinableQueue


def worker_job(q, process, lock, io_test=False, printing=False):
    '''
        this function reads the queue
        and then starts the job which is either an IO test
        or (default) a for loop with some simple calcultations
    '''
    # get the data from the queue in case it is not (can't be trusted)
    while not q.empty():
        try:
            # set a timeout and catch it as this might otherwise block forever
            data = q.get(timeout=0.1)
        except Empty:
            print "queue is empty, will shutdown process %s" % process
            return

        # lock for better printing and I/O safe
        if printing:
            lock.acquire()
            print "process", process, data
            lock.release()

        # this is the place to get the work done
        if io_test:
            # write into a dummy file and remove it afterwards
            dummyname = "tmp/" + str(process) + ".json"
            with open(dummyname, "w") as f:
                f.write(str(data))
            os.remove(dummyname)
        else:
            # just a random calcultation
            for i in range(1000):
                float(i) + random.random() * data["number"]

        # tell the queue that the task is done
        q.task_done()

    print "process %s finished with data: %s" % (process, data)
    return


def main(test_length=100000):
    # make a queue instance
    q = JoinableQueue()

    # define how many processes should be spawned
    num_proccesses = 8

    # make a lock instance for better printing and to make it I/O safe
    lock = Lock()

    # call the worker to do a job, in this case by sending a dict
    for number in range(test_length):
        q.put({"number": number})

    # start the processes
    process_list = []
    for process_number in range(num_proccesses):
        # this line differs compared to the 'threading' gist
        multi_process = Process(target=worker_job, args=(q, process_number, lock, ))
        process_list.append(multi_process)

    # start the worker
    [i.start() for i in process_list]

    # wait until all worker a finished
    [i.join() for i in process_list if i.is_alive()]

    # join the queue as well
    q.join()


if __name__ == "__main__":
    start = time.time()
    main()
    print "\n\ntime needed multiprocessing %s seconds" % (time.time() - start)
