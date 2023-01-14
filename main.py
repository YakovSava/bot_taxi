import asyncio # Импортируем асинхронность

from vkbottle.bot import Bot, Message # Импортируем объект бота и сообщени я(второе - для аннотации)
from vkbottle import CtxStorage, PhotoMessageUploader, VKAPIError
from aiohttp import ClientSession, TCPConnector
from dadata import Dadata
from pyqiwip2p import AioQiwiP2P
from sys import platform
from plugins.binder import Binder # Импортируем связыватель
from plugins.database import Database # Импортируем класс для работы с базой данных
from plugins.plotter import Plotter # Импортируем статистикуу
from plugins.keyboards import keyboards # Импортируем клавиатуры
from plugins.states import PassangerRegState, TaxiState, DeliveryState, DriverRegState,\
	VkPayPay, QiwiPay, Helper # Импорируем все стейты (для регистарций)
from plugins.forms import Forms # Импортируем формы и некоторые функции оттуда
from plugins.rules import Order, Delivery, DriverSuccess, DriverCancel, QiwiPayRule, WillArriveMinutes,\
	Arrived, VkPayRule, OffAccountRule, DeleteAccount, CancelOrder
from plugins.csveer import Csveer
from plugins.timer import Timer
from plugins.dispatcher import Dispatch
from config import vk_token, ddt_token, qiwi_token # Импрртируем токены

# try:
# 	from loguru import logger
# except ImportError:
# 	pass
# else:
# 	logger.disable("vkbottle")

try:
	import logging
except ImportError:
	pass
else:
	logging.getLogger("vkbottle").setLevel(logging.INFO)

if platform in ['win32', 'cygwin', 'msys']:
	try:
		asyncio.set_event_loop(asyncio.WindowsSelectorEventLoopPolicy())
	except:
		pass

asyncio.set_event_loop(asyncio.new_event_loop())

vk = Bot(token=vk_token) # Инициализируем класс бота
vk.on.vbml_ignore_case = True # Объявляем об игноре регистра
ddt = Dadata(ddt_token) # Инициализируем объект сервиса
binder = Binder() # Инициализируем объект связыввателя
db = Database() # Инициализируем базу данных
plot = Plotter() # Инициализируем статиста
storage = CtxStorage() # Инциализируем врмеенное хранилище
forms = Forms() # Инициализируем формы
qiwi = AioQiwiP2P(auth_key = qiwi_token)
csv = Csveer()
timer = Timer() # На будущее)
dispatcher = Dispatch(
	timer=timer,
	database=db,
	api=vk.api
)
null = None # Not debug!

# Начало бота (в группе должно стоять что бы в самом начале пользователь мог нажать на кнопку)
@vk.on.private_message(text = 'начать')
async def start_handler(message:Message):
	user = await vk.api.users.get(message.from_id)
	if (await db.passanger.exists(message.from_id)): # проверка на регистрацию... Да, сделать синхронно -  не судьба:
		await message.answer('Вы уже зарегестрированы как пассажир!', keyboard = keyboards.choose_service)
	elif (await db.driver.exists(message.from_id)):
		await message.answer('Вы уже зарегестрированы как водитель!', keyboard = keyboards.driver_registartion_success)
	elif (await dispatcher.check_registred(message.from_id)):
		await message.answer('Нужно завершить регистрацию!\nВведите ваш телефон!', keyboard=keyboards.inline.phone_pass_this_step)
		await vk.state_dispenser.set(message.from_id, DriverRegState.phone)
	else:
		await message.answer(f'Привет {user[0].first_name}!\nЯ бот-такси, помогаю пассажирам найти такси, а водителю пассажира!\n\nСоздай анкету!&#128071;&#128071;&#128071;', keyboard=keyboards.start) # А это сообщение если чеовек не зарегестрирован

@vk.on.private_message(payload = {'driver': 0, 'post_reg': 0})
async def driver_post_edit(message:Message):
	await db.driver.set_activity(message.from_id)
	await message.answer('Ожидайте новых заявок', keyboard = keyboards.driver_registartion_success)

@vk.on.private_message(payload={'on': 1})
async def on_account(message:Message):
	await dispatcher.on_account(message.from_id)
	if (await db.passanger.get(message.from_id)) is None:
		keyboard = keyboards.driver_registartion_success
		await db.driver.set_activity(message.from_id)
	else:
		keyboard = keyboards.choose_service
	await message.answer('Ваш аккаунт был снова включён, если вы хотите его отключить нажмите соответвующую кнопку на клавиатуре', keyboard=keyboard)

@vk.on.private_message(payload={'back': 0, 'not user': 0})
async def back(message:Message):
	if (await db.passanger.exists(message.from_id)):
		await message.answer('Что бы продолжить нажмите на кнопку ниже', keyboard = keyboards.choose_service)
	elif (await db.driver.exists(message.from_id)):
		await message.answer('Что бы продолжить нажмите на кнопку ниже', keyboard = keyboards.driver_registartion_success)
	elif (await dispatcher.check_registred(message.from_id)):
		state_num = int((await vk.state_dispenser.get(message.from_id)).state[-1])
		if state_num == 0:
			resume = 'номер телефона!'
			keyboard = keyboards.inline.phone_pass_this_step
		elif state_num == 1:
			resume = 'город!'
			keyboard = keyboards.inline.pass_this_step
		elif state_num == 2:
			resume = 'марку автомобиля!'
			keyboard = keyboards.empty
		elif state_num == 3:
			resume = 'цвет автомобиля!'
			keyboard = keyboards.empty
		elif state_num == 4:
			resume = 'госномер автомобиля!'
			keyboard = keyboards.empty
		await message.answer(f'Твоя анкета водителя заполнена не до конца!\n\nЗаверши создание анкеты чтобы брать заявки.\nНапиши свой {resume}', keyboard=keyboard)
	else:
		user = await vk.api.users.get(message.from_id)
		await message.answer(f'Привет {user[0].first_name}!\nЯ бот-такси, помогаю пассажирам найти такси, а водителю пассажира!\n\nСоздай анкету!&#128071;&#128071;&#128071;', keyboard=keyboards.start)

# Регистрация водителя
@vk.on.private_message(payload = {'driver': 1})
async def reg_driver_1(message:Message):
	await message.answer('Обработка...', keyboard=keyboards.empty)
	await db.driver.set_activity(message.from_id)
	await dispatcher.update_no_registred_driver(message.from_id)
	await message.answer('Продолжить можно по кнопке ниже', keyboard=keyboards.registration_failed)

@vk.on.private_message(payload={'driver': 0, 'reg': 0})
async def registartion_driver(message:Message):
	storage.set(f'{message.from_id}_balance', 0)
	await vk.state_dispenser.set(message.from_id, DriverRegState.location)
	await message.answer('Регистрация!\nТекущий город: Няндома\n\nЕсли вы из другого города, то напишите город или отправьте геолокацию', keyboard = keyboards.inline.pass_this_step)

# Отобразитьь профиль водителя
@vk.on.private_message(payload = {'driver': 0, 'profie': 0})
async def driver_profile(message:Message):
	info = await db.driver.get(message.from_id)
	parameters = await binder.get_parameters()
	if info != [None, None]:
		await db.driver.set_activity(message.from_id)
		await message.answer(f'Анкета водителя!\nВаше имя: {info[0]["name"]}\nВаш номер телефона: {info[0]["phone"]}\nВаш город: {info[0]["city"]}\nМашина: {info[0]["auto"]}\nЦвет: {info[0]["color"]}\nГосномер: {info[0]["state_number"]}\nКол-во поездок: {info[1]["quantity"]}\nБаланс: {info[1]["balance"]} руб.\nОдна заявка стоит: {parameters["count"]}', keyboard = keyboards.driver_profile)

@vk.on.private_message(OffAccountRule())
async def off_driver(message:Message):
	# await dispatcher.off_account(message.from_id)
	# await message.answer('Ваш аккаунт был отключён, больше вам не будут присылать некоторые сообщения', keyboard=keyboards.account_is_off)
	if (await db.passanger.get(message.from_id)) is None:
		await db.driver.delete(message.from_id)
	else:
		await db.passanger.delete(message.from_id)
	await message.answer()

# Редактирование (пперерегистрация водителя)
@vk.on.private_message(payload = {'driver': 0, 'edit': 0})
async def driver_edit_profile(message:Message):
	driver_profile = await db.driver.get(message.from_id)
	storage.set(f'{message.from_id}_balance', driver_profile[1]['balance'])
	await db.driver.delete(message.from_id)
	await vk.state_dispenser.set(message.from_id, DriverRegState.location)
	await message.answer('Редактирование!\n\nТекущий город: Няндома\nЕсли вы из другого города, то отправьте название вашего города или пришлите геолокацию', keyboard = keyboards.inline.pass_this_step)

# Удаление
@vk.on.private_message(DeleteAccount())
async def driver_profile_delete(message:Message):
	if (await db.passanger.get(message.from_id)) is None:
		driver_info = await db.driver.get(message.from_id)
		if driver_info[1]['balance'] > 0:
			await db.driver.set_activity(message.from_id)
			await message.answer(f'У вас на балансе есть ещё {driver_info[1]["balance"]} руб., вы можете обратиться в тех.поддержку с этим вопросом (тех.поддержка вызывается командой "техподдержка")')
		else:
			await db.driver.delete(message.from_id)
			await message.answer('Ваш профиль был удалён!\nСоздай свою анкету, жми кнопку "Начать" &#128071;&#128071;&#128071;', keyboard = keyboards.starter)
	else:
		await db.passanger.delete(message.from_id)
		await message.answer('Ваш профиль был удалён!\nСоздай свою анкету, жми кнопку "Начать" &#128071;&#128071;&#128071;', keyboard = keyboards.starter)

# профиль пассажира
@vk.on.private_message(payload = {'user': 0, 'profile': 0})
async def user_profile(message:Message):
	name = await db.passanger.get(message.from_id)
	if name is not None:
		await message.answer(f'Анкета пассажира!\n\nИмя: {name["name"]}\nТелефон: {name["phone"]}\nКол-во поездок: {name["quantity"]}\n', keyboard = keyboards.user_profile)

# Редактирование профиля пассажира
@vk.on.private_message(payload = {'user': 0, 'edit': 0})
async def passanger_edit_profile(message:Message):
	await db.passanger.delete(message.from_id)
	await vk.state_dispenser.set(message.from_id, PassangerRegState.phone)
	await message.answer('Отправьте ваш телефон для связи с водителем!\n\nТелефон можно не указывать, однако тогда водитель не сможет связаться с Вами, когда подъедет к месту вызова!', keyboard=keyboards.inline.phone_pass_this_step)

# Волшебная кнопка "назад"
@vk.on.private_message(payload = {'user': 0, 'back': 0})
async def passanger_back(message:Message):
	await message.answer('Готово!\nВыбери услугу:', keyboard = keyboards.choose_service)

# Заказ такси
@vk.on.private_message(payload = {'taxi': 0})
async def passanger_get_taxi_def(message:Message):
	await vk.state_dispenser.set(message.from_id, TaxiState.four_quest)
	await message.answer('1 - Напиши откуда и куда планируешь ехать.\n2 - Сколько человек поедет, будут ли дети\n3 - Напиши подъезд\n4 - Добавь комментарий к вызову.\nПример:\n"Ул. Ленина 8\nУл. Мира 12\nПодъезд 1\nПоедет 2 взрослых и 1 ребёнок"')

@vk.on.private_message(state = TaxiState.four_quest)
async def taxi_geo(message:Message):
	storage.set(f'{message.from_id}_taxi_get_question', message.text)
	await vk.state_dispenser.set(message.from_id, TaxiState.location)
	await message.answer('Теперь пришлите вашу геолокацию', keyboard = keyboards.inline.location)

# Непосредственно заказ такси
@vk.on.private_message(state = TaxiState.location)
async def taxi_call(message:Message):
	if message.geo is not None:
		loc = [message.geo.coordinates.latitude, message.geo.coordinates.longitude]
	else:
		loc = None
	info = await db.passanger.get(message.from_id) # Получаем данные пассажира
	text = storage.get(f'{message.from_id}_taxi_get_question')
	storage.delete(f'{message.from_id}_taxi_get_question')
	await forms.new_form(message.from_id) # Создаёи новую форму
	off_driver_ids = await dispatcher.get_service_file()
	driver_ids = [driver_id async for driver_id, driver_city in db.driver.get_all() if ((info['city'].lower() == driver_city.lower()) and (driver_id not in off_driver_ids))]
	driver_ids.extend(await dispatcher.get_no_registred_drivers())
	for driver_id in driver_ids: # Шлём всем им оповещение
		try:
			await vk.api.messages.send(
				user_id = driver_id,
				from_id = driver_id,
				random_id = 0,
				message = f'&#128293;&#128293;&#128293; Новый заказ! &#128293;&#128293;&#128293;\n\n{text}\n\nЖми кнопку &#128071;, пока никто не забрал!',
				keyboard = keyboards.inline.driver_new_order({'from_id': message.from_id, 'driver_id': driver_id, 'location': loc, 'text': text}) # P.s. смотрите файл /plugins/keyboards.py
			)
		except VKAPIError[901]:
			pass
	await message.answer(f'Ваш запрос был доставлен {len(driver_ids)} водителям\nОжидайте!', keyboard = keyboards.choose_service_before_tax) # Активных было бы считать труднее
	await vk.state_dispenser.delete(message.from_id)

# Принятие заявки
@vk.on.private_message(Order())
async def taxi_tax(message:Message):
	payload = eval(f'{message.payload}')
	if (await dispatcher.check_registred(message.from_id)):
		state_num = int((await vk.state_dispenser.get(message.from_id)).state[-1])
		if state_num == 0:
			resume = 'номер телефона!'
			keyboard = keyboards.inline.phone_pass_this_step
		elif state_num == 1:
			resume = 'город!'
			keyboard = keyboards.inline.pass_this_step
		elif state_num == 2:
			resume = 'марку автомобиля!'
			keyboard = keyboards.empty
		elif state_num == 3:
			resume = 'цвет автомобиля!'
			keyboard = keyboards.empty
		elif state_num == 4:
			resume = 'госномер автомобиля!'
			keyboard = keyboards.empty
		await message.answer(f'Твоя анкета водителя заполнена не до конца!\n\nЗаверши создание анкеты чтобы брать заявки.\nНапиши свой {resume}', keyboard=keyboard)
	else:
		await db.driver.set_activity(message.from_id)
		if await forms.get(payload['other']['from_id'])['active']: # Проверяем активна ли до сих пор форма
			parameters = await binder.get_parameters() # Получаем параметры
			driver_info = await db.driver.get(payload['other']['driver_id']) # Получаем информацию о водителе
			if int(parameters['count']) <= int(driver_info[1]['balance']): # ПРоверяем есть ли у водителя деньги
				from_id, driver_id = payload['other']['from_id'], payload['other']['driver_id']
				passanger = await db.passanger.get(from_id)
				await vk.api.messages.send(
					user_id = from_id,
					peer_id = from_id,
					random_id = 0,
					message = f'&#9989; Водитель принял ваш заказ! &#9989;\n\nТелефон водителя: {driver_info[0]["phone"]}\nМашина: {driver_info[0]["auto"]}\nЦвет: {driver_info[0]["color"]}\nГосномер: {driver_info[0]["state_number"]}\nВ конце поездки нажми "Успешно доехал"',
					keyboard = keyboards.passanger_get_taxi
				)
				await forms.start_drive(from_id, driver_id)
				await message.answer(f'Заявка принята!\nТелефон оправителя заявки: {passanger["phone"]}\n{payload["other"]["text"]}\nВот координаты отправителя заявки:', keyboard = keyboards.driver_order_complete({'from_id': from_id}))
				await asyncio.sleep(1)
				await message.answer('Мы отправили ваши контакты пассажиру!\nСкоро он свяжется с вами!')
				if payload['other']['location'] is not None:
					await asyncio.sleep(1)
					await message.answer('Вот координаты пассажира', lat = payload['other']['location'][0], long = payload['other']['location'][1])
			else:
				await message.answer(f'На вашем балансе недостаточно средств\nСтоимость одной заявки: {parameters["count"]} руб.\nНа вашем балансе: {driver_info[1]["balance"]} руб.', keyboard = keyboards.inline.payments)
		else:
			await message.answer('Кажется кто-то был быстрее тебя! &#128542;\nНе отчаивайся, скоро будет новый заказ!')

# Заказ на доставку
@vk.on.private_message(payload = {'delivery': 0})
async def get_delivery(message:Message):
	await vk.state_dispenser.set(message.from_id, DeliveryState.three_quest)
	await message.answer('Для заказа, в одном сообщении, напиши:\n1 - Что и в каком магазине купить.\n2 - Куда нужно отвезти.\n3- Сколько ты готов заплатить за доставку.\n\nУчти, чем меньше цену доставки ты предложишь, тем дольше будешь искать курьера.')

# Заполняем данные (как при заказе такси, тут схема тоно такая же)
@vk.on.private_message(state = DeliveryState.three_quest)
async def delivery_loc(message:Message):
	storage.set(f'{message.from_id}_deliver_get', message.text)
	await vk.state_dispenser.set(message.from_id, DeliveryState.location)
	await message.answer('Теперь пришлите вашу локацию', keyboard = keyboards.inline.location)

@vk.on.private_message(state = DeliveryState.location)
async def delivery_tax(message:Message):
	if message.geo is not None:
		loc = [message.geo.coordinates.latitude, message.geo.coordinates.longitude]
	else:
		loc = None
	info = await db.passanger.get(message.from_id) # Получаем данные пассажира
	await vk.state_dispenser.delete(message.from_id)
	await forms.new_form(message.from_id)
	text = storage.get(f'{message.from_id}_deliver_get')
	storage.delete(f'{message.from_id}_deliver_get')
	off_driver_ids = await dispatcher.get_service_file()
	driver_ids = [driver_id async for driver_id, driver_city in db.driver.get_all() if ((info['city'].lower() == driver_city.lower()) and (driver_id not in off_driver_ids))]
	driver_no_registred_ids = await dispatcher.get_no_registred_drivers()
	driver_ids.extend(driver_no_registred_ids)
	for driver_id in driver_ids:
		try:
			await vk.api.messages.send(
				user_id = driver_id,
				from_id = driver_id,
				random_id = 0,
				message = f'&#128640;&#128640;&#128640; Новая доставка! &#128640;&#128640;&#128640;\n\n{text}\n\nЖми кнопку &#128071;, пока никто не забрал!',
				keyboard = keyboards.inline.delivery_driver({'from_id': message.from_id, 'driver_id': driver_id, 'location': loc, 'text': text})
			)
		except VKAPIError[901]:
			pass
	await message.answer(f'Твой запрос на доставку был доставлен {len(driver_ids)} водителям', keyboard = keyboards.choose_service_before_tax)
	await vk.state_dispenser.delete(message.from_id)

# Принимаем доставку
@vk.on.private_message(Delivery())
async def driver_delivery(message:Message):
	payload = eval(f'{message.payload}')
	if (await dispatcher.check_registred(message.from_id)):
		state_num = int((await vk.state_dispenser.get(message.from_id)).state[-1])
		if state_num == 0:
			resume = 'номер телефона!'
			keyboard = keyboards.inline.phone_pass_this_step
		elif state_num == 1:
			resume = 'город!'
			keyboard = keyboards.inline.pass_this_step
		elif state_num == 2:
			resume = 'марку автомобиля!'
			keyboard = keyboards.empty
		elif state_num == 3:
			resume = 'цвет автомобиля!'
			keyboard = keyboards.empty
		elif state_num == 4:
			resume = 'госномер автомобиля!'
			keyboard = keyboards.empty
		await message.answer(f'Твоя анкета водителя заполнена не до конца!\n\nЗаверши создание анкеты чтобы брать заявки.\nНапиши свой {resume}', keyboard=keyboard)
	else:
		await db.driver.set_activity(message.from_id)
		if await forms.get(payload['other']['from_id'])['active']:
			parameters = await binder.get_parameters()
			driver_info = await db.driver.get(payload['other']['driver_id'])
			if int(parameters['count']) <= int(driver_info[1]['balance']):
				from_id, driver_id = payload['other']['from_id'], payload['other']['driver_id']
				passanger = await db.passanger.get(from_id)
				await vk.api.messages.send(
					user_id = from_id,
					peer_id = from_id,
					random_id = 0,
					message = f'&#9989; Водитель принял ваш заказ! &#9989;\n\nТелефон водителя: {driver_info[0]["phone"]}\nМашина: {driver_info[0]["auto"]}\nЦвет: {driver_info[0]["color"]}\nГосномер: {driver_info[0]["state_number"]}\n\nОжидайте доставки!',
					keyboard = keyboards.passanger_get_taxi
				)
				await forms.start_drive(from_id, driver_id)
				await message.answer(f'Заявка на доставку принята!\nТелефон оправителя заявки: {passanger["phone"]}\n{payload["other"]["text"]}\nВот координаты отправителя заявки:', keyboard = keyboards.driver_order_complete({'from_id': from_id}))
				await asyncio.sleep(1)
				await message.answer('Мы отправили ваши контакты пассажиру!\nСкоро он свяжется с вами!')
				if payload['other']['location'] is not None:
					await asyncio.sleep(1)
					await message.answer('Вот координаты пассажира', lat = payload['other']['location'][0], long = payload['other']['location'][1])
			else:
				await message.answer(f'На вашем балансе недостаточно средств\nСтоимость одной заявки: {parameters["count"]} руб.\nНа вашем балансе: {driver_info[1]["balance"]} руб.', keyboard = keyboards.inline.payments)
		else:
			await message.answer('Кажется кто-то был быстрее тебя! &#128542;\nНе отчаивайся, скоро будет новый заказ!')

# Если пассажир отменил заказ
@vk.on.private_message(payload = {'user': 0, 'cancel': 0})
async def user_cancelling_order(message:Message):
	await vk.api.messages.send(
		user_id = forms.all_forms[message.from_id]['driver_id'],
		peer_id = forms.all_forms[message.from_id]['driver_id'],
		random_id = 0,
		message = 'К сожалению пассажир отменил заказ :(\nСкоро будут ещё заявки, не отчаивайтесь!',
		keyboard = keyboards.driver_registartion_success
	)
	await forms.stop_drive(message.from_id)
	await message.answer('Вы отменили заказ!', keyboard = keyboards.choose_service)

# Если пассажир доехал
@vk.on.private_message(payload = {'user': 0, 'success': 0})
async def passanger_success_order(message:Message):
	parameters = await binder.get_parameters()
	await message.answer('Вы успешно доехали!', keyboard = keyboards.choose_service)
	await vk.api.messages.send(
		user_id = forms.all_forms[message.from_id]['driver_id'],
		peer_id = forms.all_forms[message.from_id]['driver_id'],
		random_id = 0,
		message = 'Пассажир заявил что вы доехали',
		keyboard = keyboards.driver_registartion_success
	)
	await forms.stop_drive(message.from_id)
	await db.driver.set_balance(forms.all_forms[message.from_id]['driver_id'], -parameters['count'])
	await db.driver.set_qunatity(forms.all_forms[message.from_id]['driver_id'])
	await db.passanger.set_qunatity(message.from_id)

@vk.on.private_message(DriverSuccess())
async def driver_success_order(message:Message):
	payload = eval(f'{message.payload}')
	parameters = await binder.get_parameters()
	await db.driver.set_activity(message.from_id)
	await message.answer('Вы успешно довезли пассажира!', keyboard = keyboards.driver_registartion_success)
	await vk.api.messages.send(
		user_id = payload['other']['from_id'],
		peer_id = payload['other']['from_id'],
		random_id = 0,
		message = 'Водитель заявил о том что вы доехали',
		keyboard = keyboards.choose_service
	)
	await forms.stop_drive(payload['other']['from_id'])
	await db.driver.set_balance(message.from_id, -parameters['count'])
	await db.driver.set_qunatity(message.from_id)
	await db.passanger.set_qunatity(payload['other']['from_id'])

@vk.on.private_message(WillArriveMinutes())
async def will_arived_with_minutes_with_minute(message:Message):
	await db.driver.set_activity(message.from_id)
	payload = eval(f'{message.payload}')
	await message.answer('Сообщение отправлено пассажиру!', keyboard = keyboards.driver_order_complete_will_arrive(payload['other']))
	await vk.api.messages.send(
		user_id = payload['other']['from_id'],
		peer_id = payload['other']['from_id'],
		random_id = 0,
		message = f'Водитель прибудет через {payload["minute"]} минут!'
	)

@vk.on.private_message(Arrived())
async def will_arrived(message:Message):
	await db.driver.set_activity(message.from_id)
	payload = eval(f'{message.payload}')
	await message.answer('Сообщение отправлено пассажиру!')
	await vk.api.messages.send(
		user_id = payload['other']['from_id'],
		peer_id = payload['other']['from_id'],
		random_id = 0,
		message = f'Водитель прибыл, выходите!',
		keyboard = keyboards.passanger_get_taxi_and_driver_will_arrived
	)

@vk.on.private_message(payload = {'passanger': 0, 'arrived': 0})
async def passanger_exit(message:Message):
	driver_id = await forms.get(message.from_id)['driver_id']
	await message.answer('Сообщение отправлено водителю', keyboard = keyboards.passanger_get_taxi)
	await vk.api.messages.send(
		user_id = driver_id,
		peer_id = driver_id,
		random_id = 0,
		message = 'Выхожу!'
	)

@vk.on.private_message(CancelOrder())
async def passanger_cancelling_order(message:Message):
	await forms.stop_form(message.from_id)
	await message.answer('Ваш заказ на вызов такси был отменён!', keyboard = keyboards.choose_service)

@vk.on.private_message(DriverCancel())
async def driver_cancel_order(message:Message):
	payload = eval(f'{message.payload}')
	await db.driver.set_activity(message.from_id)
	await vk.api.messages.send(
		user_id = payload['other']['from_id'],
		peer_id = payload['other']['from_id'],
		random_id = 0,
		message = 'К сожалению водитель отменил заказ :(\nВы можете заказать такси снова',
		keyboard = keyboards.choose_service
	)
	await forms.stop_drive(payload['other']['from_id'])
	await message.answer('Вы отменили заказ!', keyboard = keyboards.driver_registartion_success)

@vk.on.private_message(payload = {'driver': 0, 'money': 'vk pay'})
async def vkpay_pay(message:Message):
	await db.driver.set_activity(message.from_id)
	await vk.state_dispenser.set(message.from_id, VkPayPay.pay)
	return 'Введите сумму (только число!) которую хотите занести на ваш баланс'

@vk.on.private_message(state = VkPayPay.pay)
async def vk_pay(message:Message):
	await db.driver.set_activity(message.from_id)
	if message.text.isdigit():
		parameters = await binder.get_parameters()
		await vk.state_dispenser.delete(message.from_id)
		await message.answer(f'Ваша персональная кнопка для оплаты {message.text} руб.:', keyboard = keyboards.vk_pay_keyboard(parameters['group_id'], message.text))
	else:
		return 'Это не число. Введите сообщение снова'

@vk.on.private_message(VkPayRule())
async def pay_handler(message:Message):
	payload = dict(f'{message.payload}')
	await db.driver.set_activity(message.from_id)
	parameters = await binder.get_parameters()
	await db.driver.set_balance(message.from_id, payload['amount'])
	await message.answer(f'Вы успешно пополнили свой баланс на {payload["amount"]} руб.')
	await vk.api.messages.send(
		user_id = parameters['admin'],
		peer_id = parameters['admin'],
		random_id = 0,
		message = f'Человек @id{message.from_id} пополнил баланс на {payload["amount"]}!'
	)

@vk.on.private_message(payload = {'driver': 0, 'money': 'qiwi'})
async def qiwi_pay(message:Message):
	await db.driver.set_activity(message.from_id)
	await vk.state_dispenser.set(message.from_id, QiwiPay.pay)
	return 'Введите сумму которую хотите внести на баланс'

@vk.on.private_message(state = QiwiPay.pay)
async def qiwi_get_pay(message:Message):
	await db.driver.set_activity(message.from_id)
	if message.text.isdigit():
		bill = await qiwi.bill(
			lifetime = 15,
			amount = int(message.text),
			comment = 'Pay for BOT TAXI'
		)
		await message.answer(f'Вот ваша персональная ссылка на оплату: {bill.pay_url}\nСсылка живёт 15 минут!\n\nЧто бы проверить оплату нажмите на кнопку прикреплённую к сообщению', keyboard = keyboards.inline.qiwi_check_pay({'bill_id': bill.bill_id, 'amount': int(message.text)}))
		await vk.state_dispenser.delete(message.from_id)
	else:
		return 'Введите число!'

@vk.on.private_message(QiwiPayRule())
async def qiwi_get_pay_before_pay(message:Message):
	await db.driver.set_activity(message.from_id)
	payload = eval(f'dict({message.payload})')
	bill = await qiwi.check(payload['other']['bill_id'])
	print(bill.status)
	if bill.status != 'PAID':
		await message.answer('Вы не оплатили!')
	else:
		await message.answer(f'Вы успешно оплатили счёт в размере {payload["other"]["amount"]} руб.!', keyboard = keyboards.driver_registartion_success)
		await db.driver.set_balance(message.from_id, payload["other"]["amount"])

@vk.on.private_message(text = 'admin <commands>')
async def admin_com(message:Message, commands:str):
	parameters = await binder.get_parameters()
	if message.from_id in parameters['admin']:
		command = commands.lower().split()
		if command[0] == 'change':
			if command[1].isdigit():
				await binder.set_count(int(command[1]))
				await message.answer(f'Стоимость за одну заявку изменена на {command[1]}')
			else:
				await message.answer('Нужно ввести число!') 
		elif command[0] == 'histogram':
			await message.answer('Идёт получение данных (надолго!)')
			drivers = await db.driver.admin_get_all()
			passangers = [info async for info in db.passanger.admin_get_all()]
			csv_for_sort_histogramm, csv_for_histogram, csv_for_histogram_passangers = await asyncio.gather(
				asyncio.create_task(csv.get_csv_for_sort_histogramm([[one['name'], one['VK'], two['quntity']] for one, two in drivers])),
				asyncio.create_task(csv.get_csv_for_histogram([[one['city'], one['name']] for one, two in drivers])),
				asyncio.create_task(csv.get_csv_for_histogram_passanger([[passanger['city'], passanger['name']] for passanger in passangers]))
			)
			all_photo = await asyncio.gather(
				asyncio.create_task(plot.get_sort_histogramm(csv_for_sort_histogramm)),
				asyncio.create_task(plot.get_histogram(csv_for_histogram)),
				asyncio.create_task(plot.get_histogram_passanger(csv_for_histogram_passangers))
			)
			for photo in all_photo:
				document = await PhotoMessageUploader(vk.api).upload(photo, peer_id = message.from_id)
				await message.answer(attachment = document)
		elif command[0] == 'get':
			names = [
				[info async for info in db.passanger.admin_get_all()],
				await db.driver.admin_get_all()
			]

			csv_files = await csv.get_csv(names)
			async with ClientSession(trust_env=True, connector=TCPConnector(limit=50, force_close=True)) as session:
				for file in csv_files:
					url = await vk.api.docs.get_messages_upload_server(
						peer_id=message.from_id,
						type='doc'
					)
					async with session.post(url.upload_url, data={'file': open(file, 'rb')}) as resp:
						if resp.status == 200:
							response = await resp.json()
							try:
								data = await vk.api.docs.save(file=response['file'], title='CSV')
								await message.answer('Файл:', attachment=data.doc.url.split('?')[0])
							except KeyError:
								await message.answer(f'Что-то пошлоне так {response["error"]}')
						else:
							page = await resp.read()
							await message.answer(f'Прозошла неизвестная ошибка!\nСтатус: {resp.status}\nОшибка: {page.decode()}')
		elif command[0] == 'answer':
			if command[1].isdigit():
				message_id = await vk.api.messages.send(
					user_id = command[1],
					peer_id = command[1],
					random_id = 1,
					message = command[2]
				)
				await message.answer(f'Вы успешно ответили на вопрос {command[0]}\nЕсли вам не нравится ответ, то пропишите "admin delanswer {command[1]} {message_id}"')
			else:
				await message.answer('ID должен быть цифровой!')
		elif command[0] == 'delanswer':
			await vk.api.messages.delete(
				peer_id=command[1],
				delete_for_all=1,
				message_id=command[2]
			)
			await message.answer('Ответ был удалён!')
		elif command[0] == 'off':
			if command[1].isdigit():
				await dispatcher.off_account(int(command[1]))
				await message.answer('Успешно отключено')
			else:
				await message.answer('ID должен быть числом!')
		elif command[0] == 'mailing':
			all_chats = await vk.api.messages.get_conversations(
				offset=0,
				count=200,
				filter='all'
			)
			for chat in all_chats.items:
				await vk.api.messages.send(
					user_id=chat.conversation.peer.id,
					peer_id=chat.conversation.peer.id,
					random_id=0,
					message=message.text.split(' ', 2)[2]
				)
		else:
			await message.answer('Неизвестная команда!')

@vk.on.private_message(text='update <passer>')
async def admin_update_database(message:Message, passer:str):
	parameters = await binder.get_parameters()
	if message.from_id in parameters['admin']:
		options = passer.lower().split()
		print(options)
		if options[0] == 'passanger':
			if options[1] == 'update':
				if options[4][0] in ['+', '-', '/', '*']:
					try:
						db.passanger.cursor.execute(f'SELECT * FROM passanger WHERE VK = "{options[2]}"')
						result = db.passanger.cursor.fetchone()
						result1 = eval(f'{result[options[3]]} {options[4][0]} {options[4][1:]}')
						db.passanger.cursor.execute(f'UPDATE passanger SET {options[3]} = {result1} WHERE VK = "{options[2]}"')
						db.passanger.db.commit()
					except Exception as err:
						await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
					else:
						await message.answer('Успешно изменено!')
				else:
					try:
						db.passanger.cursor.execute(f'UPDATE passanger SET {options[3]} = "{options[4][0]}" WHERE VK = "{options[2]}"')
						db.passanger.db.commit()
					except Exception as err:
						await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
					else:
						await message.answer('Успешно изменено!')
			elif options[1] == 'delete':
				try:
					db.passanger.cursor.execute(f'DELETE FROM passanger WHERE VK = "{options[2]}"')
					db.passanger.db.commit()
				except Exception as err:
					await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
				else:
					await message.answer('Успешно удалено!')
			elif options[1] == 'reg':
				try:
					await db.passanger.reg({
						'vk': options[2],
						'gender': options[3],
						'city': options[4],
						'name': options[5],
						'phone': options[6]
					})
				except Exception as err:
					await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
				else:
					await message.answer('Успешно зарегестрировано!')
			else:
				await message.answer('Неверный оператор')
		else:
			if options[1] == 'update':
				if options[4][0] in ['+', '-', '/', '*']:
					if options[3] in ['last_activity', 'quantity', 'balance']:
						num = '2'
					else:
						num = ''
					try:
						db.driver.cursor.execute(f'SELECT * FROM driver{num} WHERE VK = "{options[2]}"')
						result = db.driver.cursor.fetchone()
						result1 = eval(f'{result[options[3]]} {options[4][0]} {options[4][1:]}')
						db.driver.cursor.execute(f'UPDATE driver{num} SET {options[3]} = {result1} WHERE VK = "{options[2]}"')
						db.driver.db.commit()
					except Exception as err:
						await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
					else:
						await message.answer('Успешно зарегестрировано!')
				else:
					if options[3] in ['last_activity', 'quantity', 'balance']:
						num = '2'
					else:
						num = ''
					try:
						db.driver.cursor.execute(f'UPDATE driver{num} SET {options[3]} = "{options[4][0]}" WHERE VK = "{options[2]}"')
						db.driver.db.commit()
					except Exception as err:
						await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
					else:
						await message.answer('Успешно зарегестрировано!')
			elif options[1] == 'delete':
				try:
					db.driver.cursor.execute(f'DELETE FROM driver WHERE VK = "{options[2]}"')
					db.driver.db.commit()
					db.driver.cursor.execute(f'DELETE FROM driver2 WHERE VK = "{options[2]}"')
					db.driver.db.commit()
				except Exception as err:
					await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
				else:
					await message.answer('Успешно удалено!')
			elif options[1] == 'reg':
				try:
					await db.driver.reg({
						'vk': options[2],
						'gender': options[3],
						'city': options[4],
						'name': options[5],
						'phone': options[6],
						'auto': options[7],
						'color': options[8],
						'state_number': options[9],
						'balance': options[10]
					})
				except Exception as err:
					await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
				else:
					await message.answer('Успешно зарегестрировано!')
			else:
				await message.answer('Неверный оператор')

@vk.on.private_message(payload={'help': 0})
async def helper(message:Message):
	await vk.state_dispenser.set(message.from_id, Helper.question)
	await message.answer('Опишите здесь то что вас интересует и вам ответят в ближайшее время')

@vk.on.private_message(state = Helper.question)
async def helper_support(message:Message):
	parameters = await binder.get_parameters()
	await vk.state_dispenser.delete(message.from_id)
	await message.answer('Ваш запрос отправлен в техподдержку')
	for admin_id in parameters['admin']:
		await vk.api.messages.send(
			user_id = admin_id,
			peer_id = admin_id,
			random_id = 0,
			message = f'ID: {message.from_id}\nВопрос: {message.text}\n\nОтветить можно командой "admin answer (ID) (message)"'
	)

# Если человек регестрируется как пассажир (шаг 1)
@vk.on.private_message(payload = {'passanger': 1})
async def reg_passanger_1(message:Message):
	await vk.state_dispenser.set(message.from_id, PassangerRegState.phone)
	await message.answer('Отправьте ваш телефон для связи с водителем!\n\nТелефон можно не указывать, однако тогда водитель не сможет связаться с Вами, когда подъедет к месту вызова!', keyboard=keyboards.inline.phone_pass_this_step)

# Регсирация пользователя (шаг 2)
@vk.on.private_message(state = PassangerRegState.phone)
async def reg_passanger_2(message:Message):
	if message.text.lower() == 'пропустить шаг':
		storage.set(f'phone_{message.from_id}', f'@id{message.from_id}')
	else:
		storage.set(f'phone_{message.from_id}', message.text)
	await vk.state_dispenser.set(message.from_id, PassangerRegState.location)
	await message.answer('Текущий город: Няндома\n\nЕсли вы хотите сменить город то напишите его название или пришлите геолокацию', keyboard = keyboards.inline.pass_this_step)

# Регистрация пользователя (шаг 3)
@vk.on.private_message(state = PassangerRegState.location)
async def reg_passanger_3(message:Message):
	if message.geo is not None: # Если геолокация отправлена
		location = message.geo.place.city
	elif message.text.lower() == 'пропустить шаг':
		location = 'няндома'
	else:
		if ddt.suggest('address', message.text) != []:
			location = message.text
		else:
			return 'Возможно вы неверно написали город!\nПопробуйте снова'
	phone = storage.get(f'phone_{message.from_id}')
	storage.delete(f'phone_{message.from_id}')
	user_data = await vk.api.users.get(
		user_ids = message.from_id,
		fields = 'sex'
	)
	await vk.state_dispenser.delete(message.from_id)
	await message.answer('Ваша анкета успешно создана!', keyboard = keyboards.choose_service)
	await db.passanger.reg({ # Непосредственно регистрация
		'vk': message.from_id,
		'gender': str(user_data[0].sex)[8:],
		'city': location,
		'name': user_data[0].first_name,
		'phone': phone
	})

# Регистрация водителя (шаг 1) 
@vk.on.private_message(state = DriverRegState.location)
async def reg_driver_loc(message:Message):
	await dispatcher.update_no_registred_driver(message.from_id)
	if message.geo is not None:
		location = message.geo.place.city
	elif message.text.lower() == 'пропустить шаг':
		location = 'няндома'
	else:
		if ddt.suggest('address', message.text) != []:
			location = message.text
		else:
			return 'Город возможно написан неверно. Попробуйте снова'
	storage.set(f'location_{message.from_id}', location)
	await vk.state_dispenser.set(message.from_id, DriverRegState.phone)
	await message.answer('Отправьте ваш телефон для связи с пассажиром!\n\nТелефон можно не указывать, однако тогда пассажир не сможет связаться с Вами, когда вы подъедете к месту вызова!', keyboard=keyboards.inline.phone_pass_this_step)

# Регистрация водителя (шаг 2)
@vk.on.private_message(state = DriverRegState.phone)
async def reg_driver_2(message:Message):
	if message.text.lower() == 'пропустить шаг':
		storage.set(f'phone_{message.from_id}', f'@id{message.from_id}')
	else:
		storage.set(f'phone_{message.from_id}', message.text)
	await vk.state_dispenser.set(message.from_id, DriverRegState.auto)
	return 'Теперь введите марку вашего авто!'

# Регистрация водителя (щаг 3)
@vk.on.private_message(state = DriverRegState.auto)
async def reg_driver_3(message:Message):
	storage.set(f'auto_{message.from_id}', message.text)
	await vk.state_dispenser.set(message.from_id, DriverRegState.color)
	return 'Теперь введите цвет'

# Регистрация водителя (шаг 4)
@vk.on.private_message(state = DriverRegState.color)
async def reg_driver_4(message:Message):
	storage.set(f'color_{message.from_id}', message.text)
	await vk.state_dispenser.set(message.from_id, DriverRegState.state_number)
	return 'И последнее - укажите госномер автомобиля'

"""
Регистрация водителя (шаг 5)

Надеюсь не булет таких людей кто напишет неверно госномер, иначе будет плохо... Наверное
"""
@vk.on.private_message(state = DriverRegState.state_number)
async def reg_driver_5(message:Message):
	await dispatcher.remove_no_registred_drivers(message.from_id)
	balance = storage.get(f'{message.from_id}_balance')
	storage.delete(f'{message.from_id}_balance')
	await vk.state_dispenser.delete(message.from_id)
	phone, auto, color, location = storage.get(f'phone_{message.from_id}'), storage.get(f'auto_{message.from_id}'), storage.get(f'color_{message.from_id}'), storage.get(f'location_{message.from_id}')
	storage.delete(f'phone_{message.from_id}'); storage.delete(f'auto_{message.from_id}'); storage.delete(f'color_{message.from_id}'); storage.delete(f'location_{message.from_id}')
	user_data = await vk.api.users.get(
		user_ids = message.from_id,
		fields = 'sex'
	)
	await db.driver.reg({ # Непсоредственная регистрация водителя
		'vk': message.from_id,
		'gender': str(user_data[0].sex)[8:],
		'city': location,
		'name': user_data[0].first_name,
		'phone': phone,
		'auto': auto,
		'color': color,
		'state_number': message.text,
		'balance': balance
	})
	await message.answer('Готово!\nТеперь когда появится новый заказ, тебе придёт уведомление, поэтому не пропусти!', keyboard = keyboards.driver_registartion_success)

@vk.on.private_message()
async def no_command(message:Message):
	some_state = await vk.state_dispenser.get(message.from_id)
	#print(some_state)
	if some_state is not None:
		await vk.state_dispenser.delete(message.from_id)
	passanger_is_exists = await db.passanger.exists(message.from_id) # проверка на регистрацию... Да, сделать синхронно -  не судьба
	driver_is_exists = await db.driver.exists(message.from_id)
	if passanger_is_exists:
		await message.answer('Неизвестная команда', keyboard = keyboards.choose_service)
	elif driver_is_exists:
		await message.answer('Неизвестная команда', keyboard = keyboards.driver_registartion_success)
	else:
		await message.answer('Пользоваться ботом могут только зарегестрированные пользователи', keyboard=keyboards.start) # А это сообщение если человек не зарегестрирован

if __name__ == '__main__':
	print('Начало работы!')
	loop = asyncio.new_event_loop()
	loop.run_until_complete(
		asyncio.wait([
			loop.create_task(dispatcher.checker()),
			loop.create_task(vk.run_polling()),
			loop.create_task(forms.cache_cleaner())
		])
	)