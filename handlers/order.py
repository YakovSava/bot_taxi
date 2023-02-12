import asyncio

from time import time
from vkbottle import CtxStorage, VKAPIError
from vkbottle.bot import Message
from plugins.keyboards import keyboards
from plugins.states import TaxiState, DeliveryState
from plugins.rules import *
from .initializer import db, dispatcher, binder
from .menu import vk

storage = CtxStorage()

@vk.on.private_message(PassangerCancelOrder())
async def user_cancelling_order(message:Message):
	payload = eval(f'{message.payload}')
	await vk.api.messages.send(
		user_id=dispatcher.all_forms[payload['key']]['driver_id'],
		peer_id=dispatcher.all_forms[payload['key']]['driver_id'],
		random_id=0,
		message = '&#9940; ПАССАЖИР ОТМЕНИЛ ЗАКАЗ &#9940;\n\
За возвратом средств за заявку, обратись к администратору группы.',
		keyboard=keyboards.driver_registartion_success
	)
	await dispatcher.stop_drive(payload['key'])
	await message.answer('Вы отменили заказ!', keyboard=keyboards.choose_service)

# Если пассажир доехал
@vk.on.private_message(PassangerSuccessOrder())
async def passanger_success_order(message:Message):
	payload = eval(f'{message.payload}')
	await message.answer('Вы успешно доехали!', keyboard=keyboards.choose_service)
	await vk.api.messages.send(
		user_id=dispatcher.all_forms[payload['key']]['driver_id'],
		peer_id=dispatcher.all_forms[payload['key']]['driver_id'],
		random_id=0,
		message='&#9989; Заявка выполнена &#9989;\nПассажир заявил, что вы успешно доехали!',
		keyboard=keyboards.driver_registartion_success
	)
	await dispatcher.stop_drive(payload['key'])
	await dispatcher.add_and_update_drive(time(), dispatcher.all_forms[payload['key']]['driver_id'])
	await dispatcher.add_and_update_drive(time(), message.from_id)

@vk.on.private_message(CancelOrder())
async def passanger_cancelling_order(message:Message):
	await dispatcher.stop_drive(eval(f'{message.payload}')['key'])
	await message.answer('Ваш вызов был отменён!', keyboard=keyboards.choose_service)

@vk.on.private_message(DriverCancel())
async def driver_cancel_order(message:Message):
	payload = eval(f'{message.payload}')
	await db.driver.set_activity(message.from_id)
	print(dispatcher.all_forms[payload['other']['key']]['data'])
	await vk.api.messages.send(
		user_id=payload['other']['from_id'],
		peer_id=payload['other']['from_id'],
		random_id=0,
		message = 'К сожалению водитель отменил заказ &#128542;\nВы можете заказать такси снова.\n\
Вы можете заказать такси снова, для этого нажмите кнопку "повторить вызов"',
		keyboard=keyboards.repeat_order(dispatcher.all_forms[payload['other']['key']]['data'])
	)
	await dispatcher.stop_drive(payload['other']['key'])
	await message.answer('&#9940; ВЫ ОТМЕНИЛИ ЗАКАЗ &#9940;', keyboard=keyboards.driver_registartion_success)

@vk.on.private_message(payload = {'delivery': 0})
async def get_delivery(message:Message):
	if (await vk.state_dispenser.get(message.from_id)) is not None:
		await vk.state_dispenser.delete(message.from_id)
	await vk.state_dispenser.set(message.from_id, DeliveryState.three_quest)
	await message.answer('Для заказа, в одном сообщении, напиши:\n\
1 - Что и в каком магазине купить.\n\
2 - Куда нужно отвезти.\n\
3- Сколько ты готов заплатить за доставку.\n\n\
Учти, чем меньше цену доставки ты предложишь, тем дольше будешь искать курьера.')

@vk.on.private_message(payload = {'taxi': 0})
async def passanger_get_taxi_def(message:Message):
	if (await vk.state_dispenser.get(message.from_id)) is not None:
		await vk.state_dispenser.delete(message.from_id)
	await vk.state_dispenser.set(message.from_id, TaxiState.four_quest)
	await message.answer('Ставь заявку так, чтобы водителям было максимально понятно твоё сообщение!\n\
\n\
1 - Напиши откуда и куда планируешь ехать.\n\
2 - Сколько человек поедет, будут ли дети.\n\
3 - Напиши подъезд.\n\
4 - Добавь комментарий к вызову.\n\
5 - Если нужно, напиши время, к которому нужно подать такси.\n\
\n\
ПРИМЕР ЗАЯВКИ:\n\
От ул. Ленина 8\n\
До ул. Мира 12\n\
Подъезд 1\n\
Поедет 2 взрослых и 1 ребёнок\n\
Подать машину к 12.30')

@vk.on.private_message(DriverSuccess())
async def driver_success_order(message:Message):
	payload = eval(f'{message.payload}')
	await db.driver.set_activity(message.from_id)
	await message.answer('&#9989; Заявка выполнена! &#9989;\nВы успешно довезли пассажира!', keyboard=keyboards.driver_registartion_success)
	await vk.api.messages.send(
		user_id=payload['other']['from_id'],
		peer_id=payload['other']['from_id'],
		random_id=0,
		message = 'Водитель заявил, что вы успешно доехали',
		keyboard=keyboards.choose_service
	)
	await dispatcher.stop_drive(payload['other']['from_id'])
	await dispatcher.add_and_update_drive(time(), message.from_id)
	await dispatcher.add_and_update_drive(time(), payload['other']['from_id'])

@vk.on.private_message(WillArriveMinutes())
async def will_arived_with_minutes_with_minute(message:Message):
	await db.driver.set_activity(message.from_id)
	payload = eval(f'{message.payload}')
	await message.answer('Сообщение отправлено пассажиру!', keyboard=keyboards.driver_order_complete_will_arrive(payload['other']))
	await vk.api.messages.send(
		user_id=payload['other']['from_id'],
		peer_id=payload['other']['from_id'],
		random_id=0,
		message=f'Водитель прибудет через {payload["minute"]} минут!'
	)

@vk.on.private_message(Arrived())
async def will_arrived(message:Message):
	payload = eval(f'{message.payload}')
	passanger_info = await db.passanger.get(payload['other']['from_id'])
	await db.driver.set_activity(message.from_id)
	await message.answer('Сообщение отправлено пассажиру!')
	await vk.api.messages.send(
		user_id=payload['other']['from_id'],
		peer_id=payload['other']['from_id'],
		random_id=0,
		message=f'Водитель прибыл, выходите!',
		keyboard=keyboards.passanger_get_taxi_and_driver_will_arrived(payload['other']['key'], passanger_info['balance'] >= 100)
	)

@vk.on.private_message(PassangerArrived())
async def passanger_exit(message:Message):
	payload = eval(f'{message.payload}')
	passanger_info = await db.passanger.get(message.from_id)
	driver_id = (await dispatcher.get(payload['key']))['driver_id']
	await message.answer('Сообщение отправлено водителю', keyboard=keyboards.passanger_get_taxi(payload['key'], passanger_info['balance'] >= 100))
	await vk.api.messages.send(
		user_id=driver_id,
		peer_id=driver_id,
		random_id=0,
		message='Выхожу!',
		keyboard=keyboards.passanger_get_taxi(payload['key'], passanger_info['balance'] >= 100)
	)

# Принятие заявки
@vk.on.private_message(Order())
async def taxi_tax(message:Message):
	payload = eval(f'{message.payload}')
	if (await dispatcher.check_registred(message.from_id)):
		state_num = int((await vk.state_dispenser.get(message.from_id)).state[-1])
		if state_num == 0:
			resume = 'номер телефона!'
			keyboard=keyboards.inline.phone_pass_this_step
		elif state_num == 1:
			resume = 'город!'
			keyboard=keyboards.inline.pass_this_step
		elif state_num == 2:
			resume = 'марку автомобиля!'
			keyboard=keyboards.empty
		elif state_num == 3:
			resume = 'цвет автомобиля!'
			keyboard=keyboards.empty
		elif state_num == 4:
			resume = 'госномер автомобиля!'
			keyboard=keyboards.empty
		await message.answer(f'Твоя анкета водителя заполнена не до конца!\n\nЗаверши создание анкеты чтобы брать заявки.\nНапиши свой {resume}', keyboard=keyboard)
	else:
		await db.driver.set_activity(message.from_id)
		if (await dispatcher.get(payload['other']['key']))['active']:
			parameters = await binder.get_parameters() # Получаем параметры
			driver_info = await db.driver.get(payload['other']['driver_id']) # Получаем информацию о водителе
			if int(parameters['count']) <= int(driver_info[1]['balance']): # ПРоверяем есть ли у водителя деньги
				await db.driver.set_balance(message.from_id, -parameters['count'])
				from_id, driver_id = payload['other']['from_id'], payload['other']['driver_id']
				passanger = await db.passanger.get(from_id)
				if driver_info[0]["phone"][:3] == "@id":
					await vk.api.messages.send(
						user_id=from_id,
						peer_id=from_id,
						random_id=0,
						message=f'&#9989; Водитель принял ваш заказ! &#9989;\n\n\
Машина: {driver_info[0]["auto"]}\n\
Цвет: {driver_info[0]["color"]}\n\
Госномер: {driver_info[0]["state_number"]}\n\
В конце поездки нажми "Успешно доехал"',
						keyboard=keyboards.passanger_get_taxi(payload['other']['key'], passanger['balance'] >= 100)
					)
					await asyncio.sleep(1)
					call_passanger = await vk.api.messages.send(
						user_id=from_id,
						peer_id=from_id,
						random_id=0,
						message=f'Кнопка для связи с водителем',
						keyboard=keyboards.inline.send(driver_id, True)
					)
				else:
					await vk.api.messages.send(
						user_id=from_id,
						peer_id=from_id,
						random_id=0,
						message=f'&#9989; Водитель принял ваш заказ! &#9989;\n\n\
Телефон: {driver_info[0]["phone"]}\n\
Машина: {driver_info[0]["auto"]}\n\
Цвет: {driver_info[0]["color"]}\n\
Госномер: {driver_info[0]["state_number"]}\n\
В конце поездки нажми "Успешно доехал"',
						keyboard=keyboards.passanger_get_taxi(payload['other']['key'], passanger['balance'] >= 100)
					)
					await asyncio.sleep(1)
					call_passanger = await vk.api.messages.send(
						user_id=from_id,
						peer_id=from_id,
						random_id=0,
						message=f'Кнопка для связи с водителем',
						keyboard=keyboards.inline.call(driver_id)
					)
				if passanger["phone"][:3] == "@id":
					await message.answer(f'&#9989; Заявка принята! &#9989;\n\n\
АДРЕС: {payload["other"]["text"]}', keyboard=keyboards.driver_order_complete({'from_id': from_id, 'key': payload['other']['key']}, [5, 10, 15]))
					call_driver = await message.answer('Звонок пассажиру (если звонки пассажиру разрешены)', keyboard=keyboards.inline.send(from_id, False))
				else:
					await message.answer(f'&#9989; Заявка принята! &#9989;\n\n\
Телефон пассажира: {passanger["phone"]}\n\
АДРЕС: {payload["other"]["text"]}', keyboard=keyboards.driver_order_complete({'from_id': from_id, 'key': payload['other']['key']}, [5, 10, 15]))
					call_driver = await message.answer('Звонок пассажиру (если звонки пассажиру разрешены)', keyboard=keyboards.inline.call(from_id,))
				if payload['other']['location'] is not None:
					await asyncio.sleep(1)
					await message.answer('Вот координаты пассажира', lat = payload['other']['location'][0], long = payload['other']['location'][1])
				dispatcher.all_forms[payload['other']['key']]['data']['driver'] = driver_id
				await asyncio.sleep(1)
				await dispatcher.start_drive(payload['other']['key'], driver_id)
				dispatcher.all_forms[payload['other']['key']]['data']['call'] = [call_passanger, call_driver.message_id]
			else:
				await message.answer(f'На вашем балансе недостаточно средств\nСтоимость одной заявки: {parameters["count"]} руб.\nНа вашем балансе: {driver_info[1]["balance"]} руб.', keyboard=keyboards.inline.payments)
		else:
			await message.answer(f'Пассажир отменил вызов или эту заявку уже принял другой водитель.', keyboard=keyboards.driver_registartion_success)

# Принимаем доставку
@vk.on.private_message(Delivery())
async def driver_delivery(message:Message):
	payload = eval(f'{message.payload}')
	if (await dispatcher.check_registred(message.from_id)):
		state_num = int((await vk.state_dispenser.get(message.from_id)).state[-1])
		if state_num == 0:
			resume = 'номер телефона!'
			keyboard=keyboards.inline.phone_pass_this_step
		elif state_num == 1:
			resume = 'город!'
			keyboard=keyboards.inline.pass_this_step
		elif state_num == 2:
			resume = 'марку автомобиля!'
			keyboard=keyboards.empty
		elif state_num == 3:
			resume = 'цвет автомобиля!'
			keyboard=keyboards.empty
		elif state_num == 4:
			resume = 'госномер автомобиля!'
			keyboard=keyboards.empty
		await message.answer(f'Твоя анкета водителя заполнена не до конца!\n\nЗаверши создание анкеты чтобы брать заявки.\nНапиши свой {resume}', keyboard=keyboard)
	else:
		await db.driver.set_activity(message.from_id)
		if (await dispatcher.get(payload['other']['key']))['active']:
			parameters = await binder.get_parameters()
			driver_info = await db.driver.get(payload['other']['driver_id'])
			if int(parameters['count']) <= int(driver_info[1]['balance']):
				await db.driver.set_balance(message.from_id, -parameters['count'])
				from_id, driver_id = payload['other']['from_id'], payload['other']['driver_id']
				passanger = await db.passanger.get(from_id)
				if driver_info[0]["phone"][:3] == "@id":
					await vk.api.messages.send(
						user_id=from_id,
						peer_id=from_id,
						random_id=0,
						message=f'&#9989; Водитель принял ваш заказ! &#9989;\n\n\
Машина: {driver_info[0]["auto"]}\n\
Цвет: {driver_info[0]["color"]}\n\
Госномер: {driver_info[0]["state_number"]}\n\
В конце поездки нажми "Успешно доехал"',
						keyboard=keyboards.passanger_get_taxi(payload['other']['key'], passanger['balance'] >= 100)
					)
					await asyncio.sleep(1)
					call_passanger = await vk.api.messages.send(
						user_id=from_id,
						peer_id=from_id,
						random_id=0,
						message=f'Кнопка для связи с водителем',
						keyboard=keyboards.inline.send(driver_id, True)
					)
				else:
					await vk.api.messages.send(
						user_id=from_id,
						peer_id=from_id,
						random_id=0,
						message=f'&#9989; Водитель принял ваш заказ! &#9989;\n\n\
Телефон: {driver_info[0]["phone"]}\n\
Машина: {driver_info[0]["auto"]}\n\
Цвет: {driver_info[0]["color"]}\n\
Госномер: {driver_info[0]["state_number"]}\n\
В конце поездки нажми "Успешно доехал"',
						keyboard=keyboards.passanger_get_taxi(payload['other']['key'], passanger['balance'] >= 100)
					)
					await asyncio.sleep(1)
					call_passanger = await vk.api.messages.send(
						user_id=from_id,
						peer_id=from_id,
						random_id=0,
						message=f'Кнопка для связи с водителем',
						keyboard=keyboards.inli(driver_id, True)
					)
				if passanger["phone"][:3] == "@id":
					await message.answer(f'&#9989; Заявка принята! &#9989;\n\n\
АДРЕС: {payload["other"]["text"]}', keyboard=keyboards.driver_order_complete({'from_id': from_id, 'key': payload['other']['key']}, [5, 10, 15]))
					call_driver = await message.answer('Звонок пассажиру (если звонки пассажиру разрешены)', keyboard=keyboards.inline.send(from_id, False))
				else:
					await message.answer(f'&#9989; Заявка принята! &#9989;\n\n\
Телефон пассажира: {passanger["phone"]}\n\
АДРЕС: {payload["other"]["text"]}', keyboard=keyboards.driver_order_complete({'from_id': from_id, 'key': payload['other']['key']}, [5, 10, 15]))
					call_driver = await message.answer('Звонок пассажиру (если звонки пассажиру разрешены)', keyboard=keyboards.inline.call(from_id))
				dispatcher.all_forms[payload['other']['key']]['data']['driver'] = driver_id
				if payload['other']['location'] is not None:
					await asyncio.sleep(1)
					await message.answer('Вот координаты пассажира', lat = payload['other']['location'][0], long = payload['other']['location'][1])
				dispatcher.all_forms[payload['other']['key']]['data']['driver'] = driver_id
				await asyncio.sleep(1)
				call_driver = await message.answer('Звонок пассажиру (если звонки пассажиру разрешены)', keyboard=keyboards.inline.call(from_id))
				dispatcher.all_forms[payload['other']['key']]['data']['call'] = [call_passanger, call_driver.message_id]
			else:
				await message.answer(f'На вашем балансе недостаточно средств\nСтоимость одной заявки: {parameters["count"]} руб.\nНа вашем балансе: {driver_info[1]["balance"]} руб.', keyboard=keyboards.inline.payments)
		else:
			await message.answer(f'Пассажир отменил вызов или эту заявку уже принял другой водитель.', keyboard=keyboards.driver_registartion_success)

@vk.on.private_message(state = DeliveryState.location)
async def delivery_tax(message:Message):
	if message.geo is not None:
		loc = [message.geo.coordinates.latitude, message.geo.coordinates.longitude]
	else:
		loc = None
	number_of_order = await dispatcher.time()
	info = await db.passanger.get(message.from_id) # Получаем данные пассажира
	key = await dispatcher.new_form(message.from_id)
	text = storage.get(f'{message.from_id}_deliver_get'); storage.delete(f'{message.from_id}_deliver_get')
	off_driver_ids = await dispatcher.get_service_file()
	driver_ids = [driver_id async for driver_id, driver_city in db.driver.get_all() if ((info['city'].lower() == driver_city.lower()) and (driver_id not in off_driver_ids))]
	driver_no_registred_ids = await dispatcher.get_no_registred_drivers()
	driver_ids.extend(driver_no_registred_ids)
	for driver_id in driver_ids:
		try:
			await vk.api.messages.send(
				user_id=driver_id,
				from_id=driver_id,
				random_id=0,
				message=f'&#128640;&#128640;&#128640; Новая доставка №{number_of_order}!\n\nАДРЕС: {text}\n\nЖми кнопку &#128071;, "принять заявку"!',
				keyboard=keyboards.inline.delivery_driver({'from_id': message.from_id, 'driver_id': driver_id, 'location': loc, 'text': text, 'key': key, 'time': number_of_order})
			)
		except VKAPIError[901]:
			pass
	await message.answer(f'Твой запрос на доставку был доставлен {len(driver_ids)} водителям', keyboard=keyboards.cancel(key))
	dispatcher.all_forms[key]['data'] = {'time': number_of_order, 'text': text, 'from_id': message.from_id, 'location': loc, 'driver': 0}
	await vk.state_dispenser.delete(message.from_id)

# Непосредственно заказ такси
@vk.on.private_message(state = TaxiState.location)
async def taxi_call(message:Message):
	if message.geo is not None:
		loc = [message.geo.coordinates.latitude, message.geo.coordinates.longitude]
	else:
		loc = None
	number_of_order = await dispatcher.time()
	info = await db.passanger.get(message.from_id) # Получаем данные пассажира
	text = storage.get(f'{message.from_id}_taxi_get_question')
	storage.delete(f'{message.from_id}_taxi_get_question')
	key = await dispatcher.new_form(message.from_id) # Создаёи новую форму
	off_driver_ids = await dispatcher.get_service_file()
	driver_ids = [driver_id async for driver_id, driver_city in db.driver.get_all() if ((info['city'].lower() == driver_city.lower()) and (driver_id not in off_driver_ids))]
	driver_ids.extend(await dispatcher.get_no_registred_drivers())
	for driver_id in driver_ids: # Шлём всем им оповещение
		try:
			await vk.api.messages.send(
				user_id=driver_id,
				from_id=driver_id,
				random_id=0,
				message=f'&#128293;&#128293;&#128293; Новый заказ №{number_of_order}!\n\nАДРЕС: {text}\n\nЖми кнопку &#128071;, "принять заявку"!',
				keyboard=keyboards.inline.driver_new_order({'from_id': message.from_id, 'driver_id': driver_id, 'location': loc, 'text': text, 'key': key, 'time': number_of_order}) # P.s. смотрите файл /plugins/keyboards.py
			)
		except VKAPIError[901]:
			pass
	await message.answer(f'Ваш запрос был доставлен {len(driver_ids)} водителям\nОжидайте!', keyboard=keyboards.cancel(key)) # Активных было бы считать труднее
	dispatcher.all_forms[key]['data'] = {'time': number_of_order, 'text': text, 'from_id': message.from_id, 'location': loc, 'driver': 0}
	await vk.state_dispenser.delete(message.from_id)

@vk.on.private_message(state = DeliveryState.three_quest)
async def delivery_loc(message:Message):
	storage.set(f'{message.from_id}_deliver_get', message.text)
	await vk.state_dispenser.set(message.from_id, DeliveryState.location)
	await message.answer('Теперь пришлите вашу локацию', keyboard=keyboards.inline.location)

@vk.on.private_message(state = TaxiState.four_quest)
async def taxi_geo(message:Message):
	storage.set(f'{message.from_id}_taxi_get_question', message.text)
	await vk.state_dispenser.set(message.from_id, TaxiState.location)
	await message.answer('Теперь пришлите вашу геолокацию', keyboard=keyboards.inline.location)

@vk.on.private_message(Repeater())
async def repeat_order(message:Message):
	payload = eval(f'{message.payload}')
	loc = payload['data']['location']
	text = payload['data']['text']
	number_of_order = await dispatcher.time()
	info = await db.passanger.get(message.from_id) # Получаем данные пассажира
	key = await dispatcher.new_form(message.from_id) # Создаёи новую форму
	off_driver_ids = await dispatcher.get_service_file()
	driver_ids = [driver_id async for driver_id, driver_city in db.driver.get_all() if ((info['city'].lower() == driver_city.lower()) and (driver_id not in off_driver_ids))]
	driver_ids.extend(await dispatcher.get_no_registred_drivers())
	try: driver_ids.remove(payload['data']['driver'])
	except ValueError: pass
	for driver_id in driver_ids: # Шлём всем им оповещение
		try:
			await vk.api.messages.send(
				user_id=driver_id,
				from_id=driver_id,
				random_id=0,
				message=f'&#128293;&#128293;&#128293; Новый заказ №{number_of_order}! &#128293;&#128293;&#128293;\n\nАДРЕС: {text}\n\nЖми кнопку &#128071;, "принять заявку"!',
				keyboard=keyboards.inline.driver_new_order({'from_id': message.from_id, 'driver_id': driver_id, 'location': loc, 'text': text, 'key': key, 'time': number_of_order}) # P.s. смотрите файл /plugins/keyboards.py
			)
		except VKAPIError[901]:
			pass
	await message.answer(f'Ваш запрос был доставлен {len(driver_ids)} водителям\nОжидайте!', keyboard=keyboards.cancel(key)) # Активных было бы считать труднее
	dispatcher.all_forms[key]['data'] = {'time': number_of_order, 'text': text, 'from_id': message.from_id, 'location': loc, 'driver': 0}

@vk.on.private_message(BonusPay())
async def passanger_pay_bonus(message:Message):
	passanger_info = await db.passanger.get(message.from_id)
	if passanger_info['balance'] >= 100:
		await message.answer('У вас накопилось 100 и более бонусных рублей. Хотите ли вы ими оплатить проезд по городу?\n\nВНИМАНИЕ\nВодитель должен быть не против оплаты бонусами!', keyboard=keyboards.pay_bonus(eval(f'{message.payload}')['key']))
	else:
		await message.answer('Подтверждение действия...', keyboard=keyboards.passanger_get_taxi(eval(f'{message.payload}')['key'], False))

@vk.on.private_message(PassangerPayBonus())
async def pasanger_pays_bomuses(message:Message):
	payload = eval(f'{message.payload}')
	form = dispatcher.all_forms[payload['key']]
	await db.driver.set_balance(form['driver_id'], 100)
	await db.passanger.set_balance(message.from_id, -100)
	await message.answer('Вы успешно оплатили поездку бонусными рублями!', keyboard=keyboards.choose_service)
	await vk.api.messages.send(
		user_id=form['driver_id'],
		peer_id=form['driver_id'],
		random_id=0,
		message='Пассажир оплатил поездку бонусными рублями, которые зачислились вам на баланс.\nЕсли вы против подобного или пассажир оплатил наличкой в машине, обратитесь в техподдержку',
		keyboard=keyboards.driver_registartion_success
	)