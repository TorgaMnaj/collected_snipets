# coding: utf-8

import sys, logging, logging.handlers, time, multiprocessing

def setLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.handlers.WatchedFileHandler('info.log')
    formatter = logging.Formatter('%(asctime)s\t%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def info(logger, message):
    logger.info(message)
    print(message)

def work(pid, name):
    logger = logging.getLogger(name)
    for i in range(50):
        info(logger, "I'm " + str(pid) + " in " + str(i) + " call")
        time.sleep(0.93)

def main():
    name = 'process'
    logger = setLogger(name)
    info(logger, 'main start')

    pool_size = 10
    process_list = [multiprocessing.Process(target=work, args=(pid,name)) for pid in range(pool_size)]
    for p in process_list: p.start()
    info(logger, 'main waiting')
    for p in process_list: p.join()
    info(logger, 'main end')

if __name__ == "__main__":
    main()
