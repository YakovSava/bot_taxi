from vkbottle import CtxStorage
from vkbottle.bot import Message
from plugins.states import PassangerRegState, DriverRegState
from plugins.keyboards import keyboards
from .initializer import ddt, db, dispatcher, binder, vk

storage = CtxStorage()

@vk.on.private_message(payload={'driver': 0, 'reg': 0})
async def registartion_driver(message:Message):
	parameters = await binder.get_parameters()
	await dispatcher.update_no_registred_driver(message.from_id)
	storage.set(f'{message.from_id}_balance', 0)
	await vk.state_dispenser.set(message.from_id, DriverRegState.location)
	await message.answer(f'Регистрация!\nТекущий город: {parameters["city"]}\n\nЕсли вы из другого города, то напишите город или отправьте геолокацию', keyboard = keyboards.inline.pass_this_step)

# Редактирование профиля пассажира
@vk.on.private_message(payload = {'user': 0, 'edit': 0})
async def passanger_edit_profile(message:Message):
	await db.passanger.delete(message.from_id)
	await vk.state_dispenser.set(message.from_id, PassangerRegState.phone)
	await message.answer('Отправьте ваш телефон для связи с водителем!\n\n\
Телефон можно не указывать, однако тогда водитель не сможет связаться с Вами, когда подъедет к месту вызова!', keyboard=keyboards.inline.phone_pass_this_step)
	
@vk.on.private_message(state = PassangerRegState.phone)
async def reg_passanger_2(message:Message):
	parameters = await binder.get_parameters()
	if message.text.lower() == 'пропустить шаг':
		storage.set(f'phone_{message.from_id}', f'@id{message.from_id}')
	else:
		storage.set(f'phone_{message.from_id}', message.text)
	await vk.state_dispenser.set(message.from_id, PassangerRegState.location)
	await message.answer(f'Текущий город: {parameters["city"]}\n\nЕсли вы хотите сменить город то напишите его название или пришлите геолокацию', keyboard = keyboards.inline.pass_this_step)

@vk.on.private_message(state = PassangerRegState.location)
async def reg_passanger_3(message:Message):
	parameters = await binder.get_parameters()
	if message.geo is not None: # Если геолокация отправлена
		storage.set(f'{message.from_id}_location', message.geo.place.city)
	elif message.text.lower() == 'пропустить шаг':
		storage.set(f'{message.from_id}_location', f'{parameters["city"]}')
	else:
		if (await ddt.suggest('address', message.text)) != []:
			storage.set(f'{message.from_id}_location', message.text.lower())
		else:
			return 'Возможно вы неверно написали город!\nПопробуйте снова'
	await vk.state_dispenser.set(message.from_id, PassangerRegState.promo)
	await message.answer('Введите пригласительный реферальный код.\nЕсли его нет - пропустите', keyboard=keyboards.inline.phone_pass_this_step)

@vk.on.private_message(state=PassangerRegState.promo)
async def insert_promo(message:Message):
	if message.text.lower() != 'пропустить шаг':
		if (await dispatcher.exists_promo(message.text)):
			if (await dispatcher.check_aipu(message.from_id)):
				await message.answer('У вас не получиться зарегестрироваться второй раз, извините')
			else:
				promo = await dispatcher.get_from_promo(message.text)
				await message.answer(f'Реферальный код от @id{promo} введён. Добро пожаловать!')
				await db.driver.set_balance(promo, 10)
				await vk.api.messages.send(
					user_id=promo,
					peer_id=promo,
					random_id=0,
					message=f'По вашему реферальному коду успешно зарегестрировался пользователь @id{message.from_id}'
				)
				await dispatcher.add_insert_promo_user(message.from_id)
		else:
			return 'Такого промокода нет. Попробуйте снова или пропустите шаг!'
	if (await vk.state_dispenser.get(message.from_id)) is not None:
		await vk.state_dispenser.delete(message.from_id)
	location = storage.get(f'{message.from_id}_location')
	phone = storage.get(f'phone_{message.from_id}')
	storage.delete(f'phone_{message.from_id}'); storage.delete(f'{message.from_id}_location')
	user_data = await vk.api.users.get(
		user_ids = message.from_id,
		fields = 'sex'
	)
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
	parameters = await binder.get_parameters()
	if message.geo is not None:
		location = message.geo.place.city
	elif message.text.lower() == 'пропустить шаг':
		location = f'{parameters["city"]}'
	else:
		if (await ddt.suggest('address', message.text)) != []:
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

# Редактирование (пперерегистрация водителя)
@vk.on.private_message(payload = {'driver': 0, 'edit': 0})
async def driver_edit_profile(message:Message):
	driver_profile = await db.driver.get(message.from_id)
	storage.set(f'{message.from_id}_balance', driver_profile[1]['balance'])
	await db.driver.delete(message.from_id)
	await vk.state_dispenser.set(message.from_id, DriverRegState.location)
	await message.answer('Редактирование!\n\nТекущий город: Няндома\nЕсли вы из другого города, то отправьте название вашего города или пришлите геолокацию', keyboard = keyboards.inline.pass_this_step)

# Если человек регестрируется как пассажир (шаг 1)
@vk.on.private_message(payload = {'passanger': 1})
async def reg_passanger_1(message:Message):
	await vk.state_dispenser.set(message.from_id, PassangerRegState.phone)
	await message.answer('Отправьте ваш телефон для связи с водителем!\n\nТелефон можно не указывать, однако тогда водитель не сможет связаться с Вами, когда подъедет к месту вызова!', keyboard=keyboards.inline.phone_pass_this_step)
