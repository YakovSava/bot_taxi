from os import listdir, getcwd
from os.path import isdir
from setuptools import Extension, setup

for file in listdir(getcwd()+'/cplug' if isdir('cplug') else getcwd()):
	if file.endswith(('.cpp', '.cxx', '.c', '.hpp', '.hh', '.cc', '.h', '.hxx', '.h++')):
		setup(
			ext_modules=[Extension(
				name=file.split('.')[0],
				sources=[file],
				language='c++'
			)]			
		)
	else:
		print(f'Cannot build {file} - That\'s not C++ source file')