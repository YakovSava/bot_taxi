import asyncio

from sys import platform
from rtoml import loads, dumps
from vkbottle.bot import Bot
from pyqiwip2p import AioQiwiP2P
from dadata import DadataAsync
from plugins.binder import Binder
from plugins.database import Database
from plugins.dispatcher import Dispatch
from plugins.timer import Timer
from plugins.csveer import Csveer

# from plugins.downoloader import DownoloadC

if platform in ['win32', 'cygwin', 'msys']:
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except:
        pass

with open('local_parameters.toml', 'r', encoding='utf-8') as file:
    local_data = loads(file.read())

with open(f'{local_data["city"]}_parameters.toml', 'w', encoding='utf-8') as file:
    file.write(dumps(local_data))

vk = Bot(
    token=local_data['token']
)

vk.on.vbml_ignore_case = True

ddt = DadataAsync(local_data['dadata'])
binder = Binder(parameters_file=f'{local_data["city"]}_parameters.toml')
db = Database()
qiwi = AioQiwiP2P(auth_key=local_data['qiwi'])
csv = Csveer()
timer = Timer()
dispatcher = Dispatch(
    timer=timer,
    database=db,
    api=vk.api
    # CGetter=DownoloadC()
)