import multiprocessing
import time


def task(i):
    # do something
    time.sleep(1)
    return i * i

def main():
    #multiprocessing.freeze_support()
    pool = multiprocessing.Pool(10)
    cpus = multiprocessing.cpu_count()
    results = []
    for i in range(0, cpus):
        result = pool.apply_async(task, args=(i,))
        print(result.get())

        results.append(result)
    pool.close()
    pool.join()
    for result in results:
        print(result.get())

main()
