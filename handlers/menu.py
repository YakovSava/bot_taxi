from vkbottle.bot import Message
from plugins.keyboards import keyboards
from plugins.states import DriverRegState
from plugins.rules import OffAccountRule, DeleteAccount
from .initializer import db, dispatcher, binder
from .registration import vk

@vk.on.private_message(text = 'начать')
async def start_handler(message:Message):
	user = await vk.api.users.get(message.from_id)
	if (await db.passanger.exists(message.from_id)):
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

@vk.on.private_message(payload = {'driver': 0, 'profie': 0})
async def driver_profile(message:Message):
	info = await db.driver.get(message.from_id)
	parameters = await binder.get_parameters()
	if info != [None, None]:
		time_record = await dispatcher.get_time_database(message.from_id)
		await db.driver.set_activity(message.from_id)
		await message.answer(f'Анкета водителя!\n\
Ваше имя: {info[0]["name"]}\n\
Ваш номер телефона: {info[0]["phone"]}\n\
Ваш город: {info[0]["city"]}\n\
Машина: {info[0]["auto"]}\n\
Цвет: {info[0]["color"]}\n\
Госномер: {info[0]["state_number"]}\n\
Кол-во поездок за 3 дня: {len(time_record["3"])}\n\
Кол-во поездок за 5 дней: {len(time_record["5"])}\n\
Кол-во поездок с ПН по ПТ: {len(time_record["week"])}\n\
Кол-во поездок за 30 дней: {len(time_record["month"])}\n\
Кол-во поездок: {info[1]["quantity"]}\n\
Баланс: {info[1]["balance"]} руб.\n\
Одна заявка стоит: {parameters["count"]}', keyboard = keyboards.driver_profile)

@vk.on.private_message(OffAccountRule())
async def off_driver(message:Message):
	# await dispatcher.off_account(message.from_id)
	await message.answer('Ваш аккаунт был отключён, больше вам не будут присылать некоторые сообщения', keyboard=keyboards.account_is_off)
	if (await db.passanger.get(message.from_id)) is None:
		await db.driver.delete(message.from_id)
	else:
		await db.passanger.delete(message.from_id)

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
		time_record = await dispatcher.get_time_database(message.from_id)
		await message.answer(f'Анкета пассажира!\n\n\
Имя: {name["name"]}\n\
Телефон: {name["phone"]}\n\
Кол-во поездок за 3 дня: {len(time_record["3"])}\n\
Кол-во поездок за 5 дней: {len(time_record["5"])}\n\
Кол-во поездок с ПН по ПТ: {len(time_record["week"])}\n\
Кол-во поездок за 30 дней: {len(time_record["month"])}\n\
Кол-во поездок: {name["quantity"]}\n', keyboard = keyboards.user_profile)

# Волшебная кнопка "назад"
@vk.on.private_message(payload = {'user': 0, 'back': 0})
async def passanger_back(message:Message):
	await message.answer('Готово!\nВыбери услугу:', keyboard = keyboards.choose_service)

@vk.on.private_message(text='тариф')
async def rate_on_city(message:Message):
	ratetext = await dispatcher.get_rate()
	await message.answer(f'Текущие тарифы:\n{ratetext}')