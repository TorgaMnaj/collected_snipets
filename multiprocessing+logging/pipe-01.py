import time
import logging
from multiprocessing import Process, Pipe, Queue

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s|%(levelname)-5.5s|%(processName)-10s| %(message)s')
logger = logging.getLogger()


def master():
    logger.info('master start')

    p, s = Pipe()

    ping_process = Process(name='ping', target=ping, args=(p,))
    ping_process.start()
    time.sleep(1)

    logger.info('master send start')
    s.send(0)
    s.send(3)
    s.send(5)
    logger.info('master send done')


def ping(p):
    logger.info('ping init')
    while True:
        args = p.recv()
        logger.info('ping %s start', args)
        time.sleep(1)
        logger.info('ping %s done', args)


master()
