import cppyy

from os import listdir
from os.path import join
from typing import Callable

class DownoloadC:

	def __init__(self):
		for file in listdir('cppplugins'):
			if file.endswith('.cxx'):
				cppyy.include(join('cppplugins', file))

	def __getattr__(self, attr_name:str) -> Callable:
		return getattr(cppyy.gbl, attr_name)