#!/usr/bin/python
import multiprocessing
import os
import subprocess
import os.path
import sys
from Queue import Empty
from multiprocessing import Process, Pool
from optparse import OptionParser
import traceback

MAX_PROCESSES = 16
unsearched = multiprocessing.Manager().Queue()
files_queue = multiprocessing.Manager().Queue()
stop_event = multiprocessing.Event()
dir_scanner_pool = None
stopped_processes_count = None

# Driectory tree crawler functions
def explore_path(path):
    directories = []
    for filename in os.listdir(path):
        fullname = os.path.join(path, filename)
        if os.path.isdir(fullname):
            directories.append(fullname)
        else:
            print "Putting " + fullname + " to files query"
            files_queue.put(fullname)
    return directories


def dir_scan_worker(task_num):
    while not unsearched.empty():
        try:
            path = unsearched.get_nowait()
            dirs = explore_path(path)
            print "Task: " + str(task_num) + " >>> Explored path: " + path
            for newdir in dirs:
                unsearched.put(newdir)
        except Empty:
            print "Task: " + str(task_num) + " reached end of the queue"
    print "Done dir_scan_worker " + str(task_num)
    unsearched.task_done()


def run_crawler(base_path):
    global dir_scanner_pool
    dir_scanner_pool = Pool(multiprocessing.cpu_count())
    if not os.path.isdir(base_path):
        raise IOError("Base path not found: " + base_path)

    cpu_count = multiprocessing.cpu_count()

    # acquire the list of all paths inside base path
    first_level_dirs = next(os.walk(base_path))[1]
    for path in first_level_dirs:
        unsearched.put(base_path + "/" + path)
    dir_scanner_pool.map_async(dir_scan_worker, range(cpu_count))
    dir_scanner_pool.close()
    # unsearched.join()


def crawler_stub(options, lock, name, is_multithread=True):
    global stopped_processes_count
    retry_count = 0
    me_stopped = False
    while not stop_event.is_set():
        try:
            print name + ": running fscat_stub on path " + files_queue.get_nowait()
        except Empty:
            print name + " reaching empty query"
            if retry_count < 3:
                print name + " retrying get file"
                time.sleep(1)
                retry_count += 1
            else:
                if stopped_processes_count.value < MAX_PROCESSES:
                    if not me_stopped:
                        lock.acquire()
                        stopped_processes_count.value += 1
                        lock.release()
                        print name + " I'm done, waiting others to complete. counter: " + str(
                            stopped_processes_count.value)
                        me_stopped = True
                    print " ************** " + name + " is still waiting. Counter: " + str(
                        stopped_processes_count.value) + "*************************"
                elif stopped_processes_count.value == MAX_PROCESSES:
                    print name + " timed out. Sending stop event"
                    stop_event.set()


def init_scanner_pool(val):
    global stopped_processes_count
    stopped_processes_count = val


def run_recursive_scan(options, results_q):
    run_crawler(options.path)
    # We're immediately start working in parallel on alredy crawled folders 
    val = multiprocessing.Manager().Value('i', 0)
    lock = multiprocessing.Manager().Lock()
    process_pool = Pool(MAX_PROCESSES, initializer=init_scanner_pool, initargs=(val,))
    for i in range(MAX_PROCESSES):
        p = process_pool.apply_async(crawler_stub, args=(options, lock, ("process-%d" % i)))
    p.get()
    process_pool.close()
    process_pool.join()

    while not results_q.empty():
        q = results_q.get()
        if q is True:  # if 'True', there is a problem
            return q
