import multiprocessing


class EasyMultiProcessing(object):
    """
    To Process the functions in parallel

    """

    def __init__(self,
                 func,
                 data,
                 *args,  # put here to enforce keyword usage

                 pool_size=None,
                 daemon=True,
                 verbose=False,

                 **kwargs
                 ):

        """

        :type kwargs: object
        :type args: object
        """
        self.func = func
        self.data = data  # must be iterable!

        # number of threads according to length of iterable, else as specified:
        if pool_size is None:
            pool_size = multiprocessing.cpu_count()

        self.verbose = verbose

        self.args = args
        self.kwargs = kwargs

        # stop sign:
        self.on = True

        # setting up and filling queue:
        self.q = multiprocessing.JoinableQueue()
        self.fill_queue(self.data)

        # initializing threads:
        self.processes = [multiprocessing.Process(target=self._processor) for _ in range(pool_size)]

        for p in self.processes:
            p.daemon = daemon

        self.print_lock = multiprocessing.Lock()

        self.sentinel = "SENTINEL"

    def _processor(self):
        # while True:  # while loop crucial here, to process all jobs in queue
        # while not self.q.empty():  # works as long queue is not empty requires external while loop
        # while self.on:  # stop sign
        while True:

            # gets task (=data item) from the queue
            task = self.q.get()

            if task == self.sentinel:
                break

            # print what process is currently working on:
            if self.verbose:
                # generating indexed thread name in the form of: func_name.thread.001:
                process_index = int(multiprocessing.current_process().name.split('-')[-1])
                process_name = self.func.__name__ + '.process.' + '{0:03d}'.format(process_index)
                with self.print_lock:
                    print('{} is working on: {}'.format(process_name, task))

            # run the job with the available worker in queue (process)
            if self.args and self.kwargs:
                self.func(task, self.args, self.kwargs)
            elif self.args:
                self.func(task, self.args)
            elif self.kwargs:
                self.func(task, self.kwargs)
            else:
                self.func(task)

            # on job completion
            self.q.task_done()
            if self.verbose:
                with self.print_lock:
                    print(('{} finished job.'.format(process_name)))

    def fill_queue(self, in_arg):
        if self.on:  # accepts input as long as stop sign is not shown
            [self.q.put(a) for a in in_arg if a is not None]
        elif not self.on:
            raise Exception('No active threads.')

    def start_all(self):
        [p.start() for p in self.processes]

    def join_all(self):
        self.on = False
        [self.q.put(self.sentinel) for _ in self.processes]  # putting sentinels in Queue
        [p.join() for p in self.processes]

