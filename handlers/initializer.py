from pyqiwip2p import AioQiwiP2P
from dadata import DadataAsync
from vkbottle import API
from plugins.binder import Binder
from plugins.database import Database
from plugins.plotter import Plotter
from plugins.dispatcher import Dispatch
from plugins.timer import Timer
from plugins.forms import Forms
from plugins.csveer import Csveer
from config import *

ddt = DadataAsync(ddt_token) # Инициализируем объект сервиса
binder = Binder() # Инициализируем объект связыввателя
db = Database() # Инициализируем базу данных
plot = Plotter() # Инициализируем статиста
forms = Forms(api=API(vk_token))
qiwi = AioQiwiP2P(auth_key=qiwi_token)
csv = Csveer()
timer = Timer()
dispatcher = Dispatch(
	timer=timer,
	database=db,
	api=API(vk_token)
)