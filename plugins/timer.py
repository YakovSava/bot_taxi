import asyncio

from threading import Thread
from typing import Callable, Coroutine

class Timer:

	def __init__(self):
		self.loop = asyncio.new_event_loop()

	def new_sync_task(self, function:Callable, *args, **kwargs):
		thread = Thread(target=function, args=args, kwargs=kwargs)
		thread.start()

	def new_async_task(self, coroutine:Coroutine, *args, **kwargs):
		thread = Thread(target=self._run_async, kwargs={'coroutine': coroutine, 'arguments': [args, kwargs]})
		thread.start()

	def _run_async(self, coroutine:Coroutine=None, arguments:dict={}):
		self.loop.run_until_complete(coroutine(*arguments[0], **arguments[1]))