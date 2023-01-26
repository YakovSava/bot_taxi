import asyncio

from threading import Thread
from time import sleep
from typing import Callable, Coroutine

class Timer:

	def __init__(self):
		pass

	def new_sync_task(self, function:Callable, *args, **kwargs):
		thread = Thread(target=function, args=args, kwargs=kwargs)
		thread.start()

	def new_async_task(self, coroutine:Coroutine, *args, **kwargs):
		proc = Thread(target=self._run_async, args=(coroutine,) + args, kwargs=kwargs)
		proc.start()

	def _run_async(self, coroutine:Coroutine, *args, **kwargs):
		sleep(10)
		asyncio.run(coroutine(*args, **kwargs))