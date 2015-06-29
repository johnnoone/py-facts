import asyncio
import logging
from .targeting import Target
from collections import OrderedDict
from .grafts import load as load_grafts, Namespace

__all__ = ['Logical']


class Logical:

    @asyncio.coroutine
    def items(self):
        """Expose all grafts.
        """

        accumulator = Accumulator()
        for graft in load_grafts():
            accumulator.spawn(graft())
        response = yield from accumulator.join()
        return response.items()

    @asyncio.coroutine
    def as_dict(self):
        data = yield from self.items()
        return OrderedDict(data)

    @asyncio.coroutine
    def read(self, target):
        data = yield from self.as_dict()
        return Target(target).read(data)

    @asyncio.coroutine
    def match(self, target):
        data = yield from self.as_dict()
        return Target(target).match(data)


class Accumulator:

    def __init__(self, *, loop=None):
        self.data = {}
        self.pending_tasks = 0
        self.loop = loop or asyncio.get_event_loop()
        self.future = asyncio.Future()
        self.processing = asyncio.Event(loop=self.loop)

    @property
    def ready(self):
        return self.pending_tasks <= 0

    def spawn(self, coro):
        self.processing.clear()
        task = asyncio.async(coro)
        task.add_done_callback(self._done)
        self.pending_tasks += 1
        return task

    def _done(self, future):
        try:
            response = future.result()
            data = self.data
            if isinstance(response, Namespace):
                namespace, response = response
                logging.info('Namespace %s', namespace)
                for part in Target(namespace):
                    data.setdefault(part, {})
                    data = data[part]

            # TODO allow nested namespace

            if response is not None:
                data.update(response)
        finally:
            self.pending_tasks -= 1
            if self.ready:
                self.processing.set()

    @asyncio.coroutine
    def join(self):
        if not self.ready:
            yield from self.processing.wait()
        return self.data
