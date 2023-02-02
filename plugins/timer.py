import asyncio

from multiprocessing import Process
from time import sleep
from typing import Callable, Coroutine

class Timer:

	def __init__(self): pass

	def new_sync_task(self, function:Callable, *args, **kwargs):
		proc = Process(target=self._time_starter, args=(function,)+args, kwargs=kwargs)
		proc.run()

	def _time_starter(self, function:Callable, *args, **kwargs):
		sleep(10)
		proc = Process(target=function, args=args, kwargs=kwargs)
		proc.run()

	def new_async_task(self, coroutine:Coroutine, *args, **kwargs):
		proc = Process(target=self._run_async, args=(coroutine,) + args, kwargs=kwargs)
		proc.run()

	def _run_async(self, coroutine:Coroutine, *args, **kwargs):
		sleep(10)
		asyncio.run(coroutine(*args, **kwargs))