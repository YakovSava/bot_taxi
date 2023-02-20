from vkbottle.bot import Message
from plugins.keyboards import keyboards
from plugins.states import DriverRegState
from plugins.rules import OffAccountRule, DeleteAccount, QuantityRule
from .initializer import db, dispatcher, binder
from .registration import vk

@vk.on.private_message(text = 'начать')
async def start_handler(message:Message):
	if (await vk.state_dispenser.get(message.from_id)) is not None:
		await vk.state_dispenser.delete(message.from_id)
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
	if (await vk.state_dispenser.get(message.from_id)) is not None:
		await vk.state_dispenser.delete(message.from_id)
	await db.driver.set_activity(message.from_id)
	await message.answer('Ожидайте новых заявок', keyboard = keyboards.driver_registartion_success)

@vk.on.private_message(payload={'back': 0, 'not user': 0})
async def back(message:Message):
	if (await vk.state_dispenser.get(message.from_id)) is not None:
		await vk.state_dispenser.delete(message.from_id)
	if (await db.passanger.exists(message.from_id)):
		await message.answer('Что бы продолжить нажмите на кнопку ниже', keyboard = keyboards.choose_service)
	elif (await db.driver.exists(message.from_id)):
		await message.answer('Что бы продолжить нажмите на кнопку ниже', keyboard = keyboards.driver_registartion_success)
	elif (await dispatcher.check_registred(message.from_id)):
		try: state_num = int((await vk.state_dispenser.get(message.from_id)).state[-1])
		except:
			resume = "нажмите на кнопку"
			keyboard = keyboards.starter
		else:
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
	if (await vk.state_dispenser.get(message.from_id)) is not None:
		await vk.state_dispenser.delete(message.from_id)
	info = await db.driver.get(message.from_id)
	parameters = await binder.get_parameters()
	if info != [None, None]:
		time_record = await dispatcher.get_time_database(message.from_id)
		await db.driver.set_activity(message.from_id)
		await message.answer(f'Анкета водителя!\n\
Ваш номер телефона: {info[0]["phone"]}\n\
Машина: {info[0]["auto"]}\n\
Цвет: {info[0]["color"]}\n\
Госномер: {info[0]["state_number"]}\n\
\n\
Кол-во поездок за 3 дня: {len(time_record["3"])}\n\
Кол-во поездок за 5 дней: {len(time_record["5"])}\n\
Кол-во поездок с ПН по ПТ: {len(time_record["week"])}\n\
Кол-во поездок за 30 дней: {len(time_record["month"])}\n\
Кол-во поездок: {info[1]["quantity"]}\n\
\n\
Баланс: {info[1]["balance"]} руб.\n\
Одна заявка стоит: {parameters["count"]}', keyboard = keyboards.driver_profile)

@vk.on.private_message(OffAccountRule())
async def off_driver(message:Message):
	if (await vk.state_dispenser.get(message.from_id)) is not None:
		await vk.state_dispenser.delete(message.from_id)
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
Телефон: {name["phone"]}\n\
\n\
Кол-во поездок за 3 дня: {len(time_record["3"])}\n\
Кол-во поездок за 5 дней: {len(time_record["5"])}\n\
Кол-во поездок с ПН по ПТ: {len(time_record["week"])}\n\
Кол-во поездок за 30 дней: {len(time_record["month"])}\n\
Кол-во поездок: {name["quantity"]}\n\
\n\
Баланс бонусных рублей {name["balance"]}', keyboard = keyboards.user_profile)

# Волшебная кнопка "назад"
@vk.on.private_message(payload = {'user': 0, 'back': 0})
async def passanger_back(message:Message):
	await message.answer('Готово!\nВыбери услугу:', keyboard = keyboards.choose_service)

@vk.on.private_message(QuantityRule())
async def rate_on_city(message:Message):
	ratetext = await dispatcher.get_rate()
	await message.answer(f'Текущие тарифы:\n{ratetext}')

@vk.on.private_message(payload={'promo': 0})
async def promos(message:Message):
	promo = await dispatcher.add_new_promo(message.from_id)
	id_ = await vk.api.groups.get_by_id()
	await message.answer('Ты можешь получить бонусные рубли на баланс анкеты, и обменять их на бесплатные поездки по городу.\n\n\
Для этого нужно переслать пригласительное сообщение друзьям. За каждую регистрацию с использованием твоего промокода ты получишь по 10р. и сможешь обменять их на поездки по городу.\n\n\
Разошли пригласительное сообщение своим друзьям &#128071;&#128071;&#128071;')
	await message.answer(f'Смотри каким ботом такси я пользуюсь: https://vk.com/write-{id_[0].id}\n\
Создай свою анкету используя мой промокод "{promo[1]}" и получи бесплатные поездки по городу!', keyboard=(keyboards.choose_service if (await db.passanger.exists(message.from_id)) else keyboards.driver_profile))

# @vk.on.private_message(payload={'promo': 0, 'add': 0})
# async def get_promo(message:Message):
# 	promo = await dispatcher.add_new_promo(message.from_id)
# 	await message.answer(f'Ваш персональный код реферальной программы: {promo[1]}\n\
# За 1 приглашённого друга +10 рублей на баланс!\n')

# @vk.on.private_message(payload={'promo': 0, 'insert': 0})
# async def insert_promo_step1(message:Message):
# 	await vk.state_dispenser.set(message.from_id, PromoState.promo)
# 	await message.answer('Напишите ваш реферальный код', keyboard=keyboards.promo_back(await db.driver.exists(message.from_id)))

# @vk.on.private_message(state=PromoState.promo)
# async def insert_promo_step2(message:Message):
# 	if (await dispatcher.exists_promo(message.text)):
# 		if (await dispatcher.check_aipu(message.from_id)):
# 			await message.answer('У вас не получиться зарегестрироваться второй раз, извините')
# 		else:
# 			promo = await dispatcher.get_from_promo(message.text)
# 			if promo == message.from_id:
# 				await message.answer('Нельзя регестрироваться, на свой же промокод')
# 			else:
# 				await vk.state_dispenser.delete(message.from_id)
# 				await message.answer(f'Реферальный код от @id{promo} введён. Добро пожаловать!')
# 				await db.driver.set_balance(promo, 10)
# 				await vk.api.messages.send(
# 					user_id=promo,
# 					peer_id=promo,
# 					random_id=0,
# 					message=f'По вашему реферальному коду успешно зарегестрировался пользователь @id{message.from_id}'
# 				)
# 				await dispatcher.add_insert_promo_user(message.from_id)
# 	else:
# 		await message.answer('Такого промокода нет. Попробуйте снова!', keyboard=keyboards.promo_back(await db.driver.exists(message.from_id)))

@vk.on.private_message(payload={'driver': 0, 'profile': 1})
async def driver_profile2(message:Message):
	await message.answer('Страница 2', keyboard=keyboards.driver_profile2)