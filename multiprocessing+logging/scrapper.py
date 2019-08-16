import queue
from multiprocessing.managers import SyncManager
from multiprocessing import Process, RLock
from bs4 import BeautifulSoup
from urllib import request 
from urllib.parse import urlparse, urljoin
from multiprocessing.managers import MakeProxyType

BaseSetProxy = MakeProxyType('BaseSetProxy', ('__and__', '__contains__', '__iand__', '__ior__', 
    '__isub__', '__ixor__', '__len__', '__or__', '__rand__', '__ror__', '__rsub__',
    '__rxor__', '__sub__', '__xor__', 'add', 'clear', 'copy', 'difference',
    'difference_update', 'discard', 'intersection', 'intersection_update', 'isdisjoint',
    'issubset', 'issuperset', 'pop', 'remove', 'symmetric_difference',
    'symmetric_difference_update', 'union', 'update'
    ))

class SetProxy(BaseSetProxy):
    # in-place hooks need to return `self`, specify these manually
    def __iand__(self, value):
        self._callmethod('__iand__', (value,))
        return self
    def __ior__(self, value):
        self._callmethod('__ior__', (value,))
        return self
    def __isub__(self, value):
        self._callmethod('__isub__', (value,))
        return self
    def __ixor__(self, value):
        self._callmethod('__ixor__', (value,))
        return self

def get_links(url):
    try:
        url_opened = request.urlopen(url)
        content = url_opened.read()
        selector = BeautifulSoup(content, "html.parser")
        links = selector.find_all('a')
        return map(lambda x: urljoin(url, x.attrs.get('href')), links)
    except:
        return []

IP = 'localhost'
PORT = 8080
AUTH_KEY = b"abcdefgs"

link_queue = queue.Queue()
crawled = set()
lock = RLock()

class JobQueueManager(SyncManager):
    pass

JobQueueManager.register('link_pool', lambda : link_queue)
JobQueueManager.register('crawled_list', lambda: crawled, SetProxy)

def working_target():
    """ target the worker """
    client = JobQueueManager(address=(IP, PORT), authkey=AUTH_KEY)
    client.connect()
    while True:
        q = client.link_pool()
        cled = client.crawled_list()
        initial = q.get()
        print(initial)
        if initial in cled:
            continue
        else:
            cled.add(initial)
        scrapped = get_links(initial)
        with lock:
            for link in scrapped:
                q.put(link)

def get_process(n):
    print("Starting {} processes".format(n))
    pids = []
    for _ in range(n):
        p = Process(target=working_target)
        p.start()
        pids.append(p)
    return pids

server = JobQueueManager(address=(IP, PORT), authkey=AUTH_KEY)

server.start()

server.link_pool().put("http://peerworld.in")

pids = get_process(100)

for pid in pids:
    pid.join()

