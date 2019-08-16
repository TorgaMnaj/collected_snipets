import time
import logging
from multiprocessing import Process, Pipe, Queue

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s|%(levelname)-5.5s|%(processName)-10s| %(message)s')
logger = logging.getLogger()


def master():
    logger.info('master start')

    p1, s1 = Pipe()
    p2, s2 = Pipe()

    ping_process = Process(name='ping', target=ping, args=(p2, s1)).start()
    pong_process = Process(name='pong', target=pong, args=(p1, s2)).start()

    time.sleep(3)
    s2.send(0)


def ping(p2, s1):
    logger.info('ping init')
    while True:
        args = p2.recv()
        logger.info('ping %s', args)
        time.sleep(1)
        ret = args
        ret = ret + 1
        s1.send(ret)

        if ret > 10:
            break


def pong(p1, s2):
    logger.info('pong init')
    while True:
        args = p1.recv()
        logger.info('pong %s', args)
        time.sleep(1)
        ret = args + 1
        s2.send(ret)
        if ret > 10:
            break

master()
