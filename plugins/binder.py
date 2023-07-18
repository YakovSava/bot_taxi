from rtoml import loads, dumps
from aiofiles import open as aiopen
from os.path import exists, isdir, join
from os import mkdir, remove
from cplug.binder import read, write


class Binder:

    def __init__(self, parameters_file: str='parameters.toml'):
        self.cache_path = 'cache'
        self.parameters_file = parameters_file
        if not isdir(self.cache_path):
            mkdir(self.cache_path)
        if not exists(self.parameters_file):
            write(parameters_file, '{}')
            self.raw_parameters = {}
        else:
            self.raw_parameters = loads(read(parameters_file))

    async def preset(self, city_name: str) -> None:
        toml_file = await self.get_parameters()
        toml_file['city'] = city_name
        async with aiopen(self.parameters_file, 'w', encoding='utf-8') as file:
            await file.write(f'{dumps(toml_file)}')

    async def get_parameters(self) -> dict:
        async with aiopen(self.parameters_file, 'r', encoding='utf-8') as file:
            lines = await file.read()
        return loads(f'{lines}')

    async def set_count(self, new_count: int) -> None:
        old_count = await self.get_parameters()
        old_count['count'] = new_count
        async with aiopen(self.parameters_file, 'w', encoding='utf-8') as file:
            await file.write(f'{dumps(old_count)}')

    async def set_buttons(self, buttons: list) -> None:
        old_count = await self.get_parameters()
        old_count['buttons'] = buttons
        async with aiopen(self.parameters_file, 'w', encoding='utf-8') as file:
            await file.write(f'{dumps(old_count)}')

    async def get_photo(self, name: str) -> bytes:
        async with aiopen(join(self.cache_path, name), 'rb') as photo_histogramm:
            photo = await photo_histogramm.read()
        remove(join(self.cache_path, name))
        return photo
