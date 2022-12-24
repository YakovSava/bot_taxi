from aiofiles import open as aiopen
from os.path import exists, isdir, join
from os import mkdir, remove

class Binder:
	
	def __init__(self):
		self.cache_path = 'cache'
		self.parameters_file = 'parameters.json'
		if not isdir(self.cache_path):
			mkdir(self.cache_path)
		if not exists(self.parameters_file):
			with open(self.parameters_file, 'w', encoding = 'utf-8') as file:
				file.write('{"admin": "", "count": 0, "group_id": 12345678}')

	async def get_parameters(self) -> dict:
		async with aiopen(self.parameters_file, 'r', encoding = 'utf-8') as file:
			lines = await file.read()
		return eval(f'dict({lines})')

	async def set_count(self, new_count:int) -> None:
		old_count = await self.get_parameters()
		old_count['count'] = new_count
		async with aiopen(self.parameters_file, 'w', encoding = 'utf-8') as file:
			await file.write(f'{old_count}')

	async def get_photo(self, name:str) -> bytes:
		async with aiopen(join(self.cache_path, name), 'rb') as photo_histogramm:
			photo = await photo_histogramm.read()
		remove(join(self.cache_path, name))
		return photo