from vkbottle.bot import Message
from .initializer import db, qiwi, binder
from plugins.keyboards import keyboards
from plugins.states import *
from plugins.rules import *
from plugins.yoomoney_pay import Yoomoney
from .admin import vk

ym = Yoomoney()

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
	payload = eval(f'{message.payload}')
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

@vk.on.private_message(payload = {'driver': 0, 'money': 'yoomoney'})
async def yoomoney_pay(message:Message):
	await db.driver.set_activity(message.from_id)
	await vk.state_dispenser.set(message.from_id, YoomoneyPay.pay)
	return 'Введите сумму которую хотите внести на баланс'

@vk.on.private_message(state = YoomoneyPay.pay)
async def yoomoney_get_pay(message:Message):
	await db.driver.set_activity(message.from_id)
	if message.text.isdigit():
		if int(message.text) < 2:
			return "Минимальная сумма пополнения: 3"
	if message.text.isdigit():
		url, label = ym.build_quickpay(int(message.text))
		await message.answer(f'Вот ваша персональная ссылка на оплату: {url}\nСсылка живёт 15 минут!\n\nЧто бы проверить оплату нажмите на кнопку прикреплённую к сообщению', keyboard = keyboards.inline.yoomoney_check_pay({'bill_id': label, 'amount': int(message.text)}))
		await vk.state_dispenser.delete(message.from_id)
	else:
		return 'Введите число!'

@vk.on.private_message(YoomoneyPayRule())
async def yoomoney_get_pay_before_pay(message:Message):
	await db.driver.set_activity(message.from_id)
	payload = eval(f'dict({message.payload})')
	status = ym.check_pay(payload['other']['bill_id'])
	if not status:
		await message.answer('Вы не оплатили!')
	else:
		await message.answer(f'Вы успешно оплатили счёт в размере {payload["other"]["amount"]} руб.!', keyboard = keyboards.driver_registartion_success)
		await db.driver.set_balance(message.from_id, payload["other"]["amount"])