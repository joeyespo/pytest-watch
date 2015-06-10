# -*- coding: utf-8

from multiprocessing import Queue, Process, Event


class Timer(Process):
    def __init__(self, interval, function, args=[], kwargs={}):
        super(Timer, self).__init__()
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()

    def cancel(self):
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()


class EventSpooler(object):
    def __init__(self, cooldown, callback):
        self.cooldown = cooldown
        self.callback = callback
        self.inbox = Queue()
        self.outbox = Queue()

    def enqueue(self, event):
        self.inbox.put(event)
        Timer(self.cooldown, self.process).start()

    def process(self):
        self.outbox.put(self.inbox.get())
        if self.inbox.empty():
            events = []
            while not self.outbox.empty():
                events.append(self.outbox.get())
            self.callback(events)
