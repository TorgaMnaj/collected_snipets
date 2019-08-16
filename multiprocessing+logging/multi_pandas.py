#!/Applications/Anaconda3/anaconda/bin/python
#author: Stefano Manzini; stefano.manzini@gmail.com

# Python multiprocessing library example script

import multiprocessing
from random import randint
from random import uniform as randfloat
import time
import pandas as pd

# a little setup
cores = 4
pd.DataFrame({"data" : [randint(0,100) for x in range(20)]}).to_csv("data.csv")

# ==

def print_counter(counter):
    """multiprocessing.Value returns a <ctypes> object allocated from shared
    memory, sayeth the doc. We made it a signed integer ("i")."""
    while True:
        print("Counter is now: ", counter.value, "\r", end = "")
        time.sleep(0.25)


def do_work(counter, lock, queue, df):    
    name = multiprocessing.current_process().name
    new_data = []   # this will store processed data
    made_by = []
    timestamp = []
    
    for data in df["data"]:    # not discussing df.applymap() here
        new_data.append(data ** 3)  # we're transforming our input data
        made_by.append(name)
        timestamp.append(time.ctime())
        
        # counter update
        with lock:
            counter.value += 1
        
        time.sleep(randfloat(0.1, 1))
    
    print("worker:", name, "reports: WORK DONE")
    new_df = pd.DataFrame({"old_data" : df["data"],
                           "new_data" : new_data,
                           "made_by" : made_by,
                           "timestamp" : timestamp
                           }
    )
    queue.put(new_df)

# ==

if __name__ == "__main__":

    workers = []
    counter = multiprocessing.Value("i", 0)
    lock = multiprocessing.Lock()
    output_queue = multiprocessing.Queue()
    
    # we already know our data table is 20 rows tall, so we divide it into
    # four even chunks, 5 rows each (each core will be fed one DataFrame chunk)
    df = pd.read_csv("data.csv", index_col = 0, chunksize = 5)
    
    for i, df_chunk in zip(range(cores), df):
        p = multiprocessing.Process(
            name = ("Process " + str(i)),
            target = do_work,
            kwargs = {"df" : df_chunk,
                      "counter" : counter,
                      "lock" : lock,
                      "queue" : output_queue        
            }
        )
        workers.append(p)
        p.start()
    
    counter_printer_worker = multiprocessing.Process(
        target = print_counter,
        kwargs = {"counter" : counter}
    )
    counter_printer_worker.start()
    
    for w in workers:
        w.join()
    
    counter_printer_worker.terminate()
    
    print("All workers have terminated their job now.")
    
    result = [output_queue.get() for i in range(cores)]
    final_df = pd.concat(result)
    
    print("\nFinal output of all workers:\n", final_df)