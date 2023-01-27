from time import time
from vkbottle import CtxStorage, VKAPIError
from vkbottle.bot import BotLabeler, Message
from .initializer import db, dispatcher, forms, api
from plugins.keyboards import keyboards
from plugins.states import TaxiState, DeliveryState
from plugins.rules import *

vk = BotLabeler()
storage = CtxStorage()

@vk.private_message(PassangerCancelOrder())
async def user_cancelling_order(message:Message):
	payload = eval(f'{message.payload}')
	await api.messages.send(
		user_id = forms.all_forms[payload['key']]['driver_id'],
		peer_id = forms.all_forms[payload['key']]['driver_id'],
		random_id = 0,
		message = '&#9940; ПАССАЖИР ОТМЕНИЛ ЗАКАЗ &#9940;\n\
За возвратом средств за заявку, обратись к администратору группы.',
		keyboard = keyboards.driver_registartion_success
	)
	await forms.stop_drive(payload['key'])
	await message.answer('Вы отменили заказ!', keyboard = keyboards.choose_service)

# Если пассажир доехал
@vk.private_message(PassangerSuccessOrder())
async def passanger_success_order(message:Message):
	payload = eval(f'{message.payload}')
	await message.answer('Вы успешно доехали!', keyboard = keyboards.choose_service)
	await api.messages.send(
		user_id = forms.all_forms[payload['key']]['driver_id'],
		peer_id = forms.all_forms[payload['key']]['driver_id'],
		random_id = 0,
		message = '&#9989; Заявка выполнена &#9989;\nПассажир заявил, что вы успешно доехали!',
		keyboard = keyboards.driver_registartion_success
	)
	await forms.stop_drive(payload['key'])
	await dispatcher.add_and_update_drive(time(), forms.all_forms[payload['key']]['driver_id'])
	await dispatcher.add_and_update_drive(time(), message.from_id)

@vk.private_message(CancelOrder())
async def passanger_cancelling_order(message:Message):
	await forms.stop_drive(eval(f'{message.payload}')['key'])
	await message.answer('Ваш вызов был отменён!', keyboard = keyboards.choose_service)

@vk.private_message(DriverCancel())
async def driver_cancel_order(message:Message):
	payload = eval(f'{message.payload}')
	await db.driver.set_activity(message.from_id)
	await api.messages.send(
		user_id = payload['other']['from_id'],
		peer_id = payload['other']['from_id'],
		random_id = 0,
		message = 'К сожалению водитель отменил заказ &#128542;\nВы можете заказать такси снова',
		keyboard = keyboards.choose_service
	)
	await forms.stop_drive(payload['other']['key'])
	await message.answer('&#9940; ВЫ ОТМЕНИЛИ ЗАКАЗ &#9940;\n\
За возвратом средств за заявку, обратись к администратору группы.', keyboard = keyboards.driver_registartion_success)

@vk.private_message(DriverSuccess())
async def driver_success_order(message:Message):
	payload = eval(f'{message.payload}')
	await db.driver.set_activity(message.from_id)
	await message.answer('&#9989; Заявка выполнена! &#9989;\nВы успешно довезли пассажира!', keyboard = keyboards.driver_registartion_success)
	await api.messages.send(
		user_id = payload['other']['from_id'],
		peer_id = payload['other']['from_id'],
		random_id = 0,
		message = 'Водитель заявил о том что вы доехали',
		keyboard = keyboards.choose_service
	)
	await forms.stop_drive(payload['other']['from_id'])
	await dispatcher.add_and_update_drive(time(), message.from_id)
	await dispatcher.add_and_update_drive(time(), payload['other']['from_id'])

@vk.private_message(WillArriveMinutes())
async def will_arived_with_minutes_with_minute(message:Message):
	await db.driver.set_activity(message.from_id)
	payload = eval(f'{message.payload}')
	await message.answer('Сообщение отправлено пассажиру!', keyboard = keyboards.driver_order_complete_will_arrive(payload['other']))
	await api.messages.send(
		user_id = payload['other']['from_id'],
		peer_id = payload['other']['from_id'],
		random_id = 0,
		message = f'Водитель прибудет через {payload["minute"]} минут!'
	)

@vk.private_message(Arrived())
async def will_arrived(message:Message):
	payload = eval(f'{message.payload}')
	await db.driver.set_activity(message.from_id)
	await message.answer('Сообщение отправлено пассажиру!')
	await api.messages.send(
		user_id = payload['other']['from_id'],
		peer_id = payload['other']['from_id'],
		random_id = 0,
		message = f'Водитель прибыл, выходите!',
		keyboard = keyboards.inline.passanger_get_taxi_and_driver_will_arrived(payload['other']['key'])
	)

@vk.private_message(PassangerArrived())
async def passanger_exit(message:Message):
	payload = eval(f'{message.payload}')
	driver_id = (await forms.get(payload['key']))['driver_id']
	await message.answer('Сообщение отправлено водителю', keyboard = keyboards.inline.passanger_get_taxi(payload['key']))
	await api.messages.send(
		user_id = driver_id,
		peer_id = driver_id,
		random_id = 0,
		message = 'Выхожу!'
	)

# Принятие заявки
@vk.private_message(Order())
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
		if (await forms.get(payload['other']['key']))['active']: # Проверяем активна ли до сих пор форма
			number_of_order = await dispatcher.get_order_names()
			await dispatcher.set_order_names()
			parameters = await binder.get_parameters() # Получаем параметры
			driver_info = await db.driver.get(payload['other']['driver_id']) # Получаем информацию о водителе
			if int(parameters['count']) <= int(driver_info[1]['balance']): # ПРоверяем есть ли у водителя деньги
				await db.driver.set_balance(message.from_id, -parameters['count'])
				from_id, driver_id = payload['other']['from_id'], payload['other']['driver_id']
				passanger = await db.passanger.get(from_id)
				await api.messages.send(
					user_id = from_id,
					peer_id = from_id,
					random_id = 0,
					message = f'&#9989; Водитель принял ваш заказ! &#9989;\n\n\
Телефон водителя: {"vk.me/"+driver_info[0]["phone"][1:] if driver_info[0]["phone"][:3] == "@id" else driver_info[0]["phone"]}\n\
Машина: {driver_info[0]["auto"]}\n\
Цвет: {driver_info[0]["color"]}\n\
Госномер: {driver_info[0]["state_number"]}\n\
В конце поездки нажми "Успешно доехал"',
					keyboard = keyboards.inline.passanger_get_taxi(payload['other']['key'])
				)
				await forms.start_drive(payload['other']['key'], driver_id)
				await message.answer(f'&#9989; Заявка {number_of_order} принята! &#9989;\n\nТелефон пассажира: {"vk.me/"+passanger["phone"][1:] if passanger["phone"][:3] == "@id" else passanger["phone"]}\nАДРЕС: {payload["other"]["text"]}', keyboard = keyboards.driver_order_complete({'from_id': from_id, 'key': payload['other']['key']}))
				# await asyncio.sleep(1)
				# await message.answer('Мы отправили ваши контакты пассажиру!\nСкоро он свяжется с вами!')
				if payload['other']['location'] is not None:
					await asyncio.sleep(1)
					await message.answer('Вот координаты пассажира', lat = payload['other']['location'][0], long = payload['other']['location'][1])
			else:
				await message.answer(f'На вашем балансе недостаточно средств\nСтоимость одной заявки: {parameters["count"]} руб.\nНа вашем балансе: {driver_info[1]["balance"]} руб.', keyboard = keyboards.inline.payments)
		else:
			await message.answer('Другой водитель уже принял эту заявку!')

# Принимаем доставку
@vk.private_message(Delivery())
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
		if (await forms.get(payload['other']['key']))['active']:
			parameters = await binder.get_parameters()
			driver_info = await db.driver.get(payload['other']['driver_id'])
			if int(parameters['count']) <= int(driver_info[1]['balance']):
				number_of_order = await dispatcher.get_order_names()
				await dispatcher.set_order_names()
				await db.driver.set_balance(message.from_id, -parameters['count'])
				from_id, driver_id = payload['other']['from_id'], payload['other']['driver_id']
				passanger = await db.passanger.get(from_id)
				await api.messages.send(
					user_id = from_id,
					peer_id = from_id,
					random_id = 0,
					message = f'&#9989; Водитель принял ваш заказ! &#9989;\n\n\
Телефон водителя: {"vk.me/"+driver_info[0]["phone"][1:] if driver_info[0]["phone"][:3] == "@id" else driver_info[0]["phone"]}\n\
Машина: {driver_info[0]["auto"]}\n\
Цвет: {driver_info[0]["color"]}\n\
Госномер: {driver_info[0]["state_number"]}\n\n\
Ожидайте доставки!',
					keyboard = keyboards.inline.passanger_get_taxi(payload['other']['key'])
				)
				await forms.start_drive(payload['other']['key'], driver_id)
				await message.answer(f'&#9989; Заявка на доставку {number_of_order} принята! &#9989;\n\
АДРЕС: {payload["other"]["text"]}\n\
Телефон пассажира: {"vk.me/"+passanger["phone"][1:] if passanger["phone"][:3] == "@id" else passanger["phone"]}', keyboard = keyboards.driver_order_complete({'from_id': from_id, 'key': payload['other']['key']}))
				# await asyncio.sleep(1)
				# await message.answer('Мы отправили ваши контакты пассажиру!\nСкоро он свяжется с вами!')
				if payload['other']['location'] is not None:
					await asyncio.sleep(1)
					await message.answer('Вот координаты пассажира', lat = payload['other']['location'][0], long = payload['other']['location'][1])
			else:
				await message.answer(f'На вашем балансе недостаточно средств\nСтоимость одной заявки: {parameters["count"]} руб.\nНа вашем балансе: {driver_info[1]["balance"]} руб.', keyboard = keyboards.inline.payments)
		else:
			await message.answer('Другой водитель уже принял эту заявку!')

@vk.private_message(state = DeliveryState.location)
async def delivery_tax(message:Message):
	if message.geo is not None:
		loc = [message.geo.coordinates.latitude, message.geo.coordinates.longitude]
	else:
		loc = None
	info = await db.passanger.get(message.from_id) # Получаем данные пассажира
	await vk.state_dispenser.delete(message.from_id)
	key = await forms.new_form(message.from_id)
	text = storage.get(f'{message.from_id}_deliver_get'); storage.delete(f'{message.from_id}_deliver_get')
	off_driver_ids = await dispatcher.get_service_file()
	driver_ids = [driver_id async for driver_id, driver_city in db.driver.get_all() if ((info['city'].lower() == driver_city.lower()) and (driver_id not in off_driver_ids))]
	driver_no_registred_ids = await dispatcher.get_no_registred_drivers()
	driver_ids.extend(driver_no_registred_ids)
	for driver_id in driver_ids:
		try:
			await api.messages.send(
				user_id = driver_id,
				from_id = driver_id,
				random_id = 0,
				message = f'&#128640;&#128640;&#128640; Новая доставка! &#128640;&#128640;&#128640;\n\nАДРЕС: {text}\n\nЖми кнопку &#128071;, "принять заявку"!',
				keyboard = keyboards.inline.delivery_driver({'from_id': message.from_id, 'driver_id': driver_id, 'location': loc, 'text': text, 'key': key})
			)
		except VKAPIError[901]:
			pass
	await message.answer(f'Твой запрос на доставку был доставлен {len(driver_ids)} водителям', keyboard = keyboards.cancel(key))

# Непосредственно заказ такси
@vk.private_message(state = TaxiState.location)
async def taxi_call(message:Message):
	if message.geo is not None:
		loc = [message.geo.coordinates.latitude, message.geo.coordinates.longitude]
	else:
		loc = None
	info = await db.passanger.get(message.from_id) # Получаем данные пассажира
	text = storage.get(f'{message.from_id}_taxi_get_question')
	storage.delete(f'{message.from_id}_taxi_get_question')
	key = await forms.new_form(message.from_id) # Создаёи новую форму
	off_driver_ids = await dispatcher.get_service_file()
	driver_ids = [driver_id async for driver_id, driver_city in db.driver.get_all() if ((info['city'].lower() == driver_city.lower()) and (driver_id not in off_driver_ids))]
	driver_ids.extend(await dispatcher.get_no_registred_drivers())
	for driver_id in driver_ids: # Шлём всем им оповещение
		try:
			await api.messages.send(
				user_id = driver_id,
				from_id = driver_id,
				random_id = 0,
				message = f'&#128293;&#128293;&#128293; Новый заказ! &#128293;&#128293;&#128293;\n\nАДРЕС: {text}\n\nЖми кнопку &#128071;, "принять заявку"!',
				keyboard = keyboards.inline.driver_new_order({'from_id': message.from_id, 'driver_id': driver_id, 'location': loc, 'text': text, 'key': key}) # P.s. смотрите файл /plugins/keyboards.py
			)
		except VKAPIError[901]:
			pass
	await message.answer(f'Ваш запрос был доставлен {len(driver_ids)} водителям\nОжидайте!', keyboard = keyboards.cancel(key)) # Активных было бы считать труднее

@vk.private_message(state = DeliveryState.three_quest)
async def delivery_loc(message:Message):
	storage.set(f'{message.from_id}_deliver_get', message.text)
	await vk.state_dispenser.set(message.from_id, DeliveryState.location)
	await message.answer('Теперь пришлите вашу локацию', keyboard = keyboards.inline.location)

@vk.private_message(state = TaxiState.four_quest)
async def taxi_geo(message:Message):
	storage.set(f'{message.from_id}_taxi_get_question', message.text)
	await vk.state_dispenser.set(message.from_id, TaxiState.location)
	await message.answer('Теперь пришлите вашу геолокацию', keyboard = keyboards.inline.location)

@vk.private_message(payload = {'delivery': 0})
async def get_delivery(message:Message):
	await vk.state_dispenser.set(message.from_id, DeliveryState.three_quest)
	await message.answer('Для заказа, в одном сообщении, напиши:\n\
1 - Что и в каком магазине купить.\n\
2 - Куда нужно отвезти.\n\
3- Сколько ты готов заплатить за доставку.\n\n\
Учти, чем меньше цену доставки ты предложишь, тем дольше будешь искать курьера.')

@vk.private_message(payload = {'taxi': 0})
async def passanger_get_taxi_def(message:Message):
	await vk.state_dispenser.set(message.from_id, TaxiState.four_quest)
	await message.answer('1 - Напиши откуда и куда планируешь ехать.\n\
2 - Сколько человек поедет, будут ли дети\n3 - Напиши подъезд\n\
4 - Добавь комментарий к вызову.\n\
Пример:\n"Ул. Ленина 8\nУл. Мира 12\nПодъезд 1\nПоедет 2 взрослых и 1 ребёнок"')