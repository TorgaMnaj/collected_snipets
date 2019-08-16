import multiprocessing as mp
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s|%(levelname)-5.5s|%(processName)-10s| %(message)s')
logger = logging.getLogger()

q = mp.Queue(2)


# put, if queue is full, then block process
# put_nowait, if queue is full, then raise Queue.Full Exception.


q.put([0])
q.put_nowait([0, 1])
q.put_nowait([0, 1, 2])

print q.get()
print q.get()
print q.get()
