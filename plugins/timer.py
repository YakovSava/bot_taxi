import asyncio

from threading import Thread
from typing import Callable, Coroutine

class Timer:

	def __init__(self):
		pass

	def new_sync_task(self, function:Callable, *args, **kwargs):
		thread = Thread(target=function, args=args, kwargs=kwargs)
		thread.start()

	def new_async_task(self, coroutine:Coroutine, *args, **kwargs):
		thread = Thread(target=self._run_async, kwargs={'coroutine': coroutine, 'arguments': [args, kwargs]})
		thread.start()

	def _run_async(self, coroutine:Coroutine=None, arguments:list=[]):
		asyncio.run(coroutine(*arguments[0], **arguments[1]))