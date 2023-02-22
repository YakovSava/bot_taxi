from vkbottle import Keyboard, KeyboardButtonColor, Text, VKPay, Location, EMPTY_KEYBOARD, OpenLink

class keyboards:
	empty = EMPTY_KEYBOARD
	class inline:
		delivery_driver = lambda x: (Keyboard(one_time = False, inline = True)
			.add(Text('Принять доставку &#128526;', payload={'driver': 0, 'delivery': 1, 'other': x}), color=KeyboardButtonColor.POSITIVE)
		).get_json()
		driver_new_order = lambda x: (Keyboard(one_time = False, inline = True)
			.add(Text('Принять заявку &#128526;', payload={'driver': 1, 'order': 1, 'other': x}), color=KeyboardButtonColor.POSITIVE)
		).get_json()
		qiwi_check_pay = lambda x: (Keyboard(one_time = False, inline = True)
			.add(Text('Проверить оплату', payload={'driver': 0, 'qiwi': 0, 'other': x}), color=KeyboardButtonColor.PRIMARY)
		).get_json()
		location = (Keyboard(one_time = False, inline = True)
			.add(Location(), color=KeyboardButtonColor.PRIMARY)
			.row()
			.add(Text('Пропустить шаг'), color=KeyboardButtonColor.POSITIVE)
		).get_json()
		payments = (Keyboard(one_time = False, inline = True)
			# .add(Text('Пополнить при помощи VK PAY', payload={'driver': 0, 'money': 'vk pay'}), color=KeyboardButtonColor.POSITIVE)
			# .row()
			.add(Text('Пополнить при помощи QIWI', payload={'driver': 0, 'money': 'qiwi'}), color=KeyboardButtonColor.POSITIVE)
			.row()
			.add(Text('Принимать заявки', payload={'driver': 0, 'post_reg': 0}), color=KeyboardButtonColor.POSITIVE)
		).get_json()
		pass_this_step = (Keyboard(one_time=False, inline=True)
			.add(Text('Пропустить шаг'), color=KeyboardButtonColor.POSITIVE)
			.row()
			.add(Location(), color=KeyboardButtonColor.PRIMARY)
		).get_json()
		phone_pass_this_step = (Keyboard(one_time=False, inline=True)
			.add(Text('Пропустить шаг'), color=KeyboardButtonColor.POSITIVE)
		).get_json()
		resume_reg = (Keyboard(one_time=False, inline=True)
			.add(Text('Продолжить регистрацию', payload={'resume': 0}), color=KeyboardButtonColor.POSITIVE)
		).get_json()
		call = lambda from_id: (Keyboard(inline=True)
			.add(OpenLink(f'https://vk.com/call?id={from_id}', f'Позвонить в ВК'), color=KeyboardButtonColor.PRIMARY)
		)
		send = lambda from_id, driver: (Keyboard(inline=True)
			.add(OpenLink(f'https://vk.com/call?id={from_id}', f'Позвонить в ВК'), color=KeyboardButtonColor.PRIMARY)
			.row()
			.add(OpenLink(f'https://vk.me/id{from_id}', f'Написать {("водителю" if driver else "пассажиру")}'), color=KeyboardButtonColor.PRIMARY)
		)

	repeat_order_before_driver_cancel_order = lambda data: (Keyboard()
		.add(Text('Повторить вызов', payload={'repeat': 0, 'data': data}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Назад', payload={'user': 0, 'back': 0}), color=KeyboardButtonColor.PRIMARY)
	).get_json()
	passanger_get_taxi = lambda key, bonus: (Keyboard(one_time = False, inline=False)
		.add(Text('Отменить вызов', payload={'user': 0, 'cancel': 0, 'key': key}), color=KeyboardButtonColor.NEGATIVE)
		.row()
		.add(Text('Успешно доехал', payload={'user': 0, 'success': 0, 'key': key} if not bonus else {'user': 0, 'pay': 0, 'bonus': 0, 'key': key}), color=KeyboardButtonColor.POSITIVE)
	).get_json()
	passanger_get_taxi_and_driver_will_arrived = lambda key, bonus: (Keyboard(one_time = False, inline=False)
		.add(Text('Выхожу!', payload={'passanger': 0, 'arrived': 0, 'key': key}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text('Отменить вызов', payload={'user': 0, 'cancel': 0, 'key': key}), color=KeyboardButtonColor.NEGATIVE)
		.row()
		.add(Text('Успешно доехал', payload={'user': 0, 'success': 0, 'key': key} if not bonus else {'user': 0, 'pay': 0, 'bonus': 0, 'key': key}), color=KeyboardButtonColor.POSITIVE)
	).get_json()
	cancel = lambda key: (Keyboard(one_time=False, inline=False)
		.add(Text('Отменить заказ', payload={'passager': 0, 'cancel': 0, 'taxi': 0, 'key': key}), color=KeyboardButtonColor.NEGATIVE)
	).get_json()
	driver_registartion_success = (Keyboard(one_time=True, inline=False)
		.add(Text('Моя анкета &#128526;', payload={'driver': 0, 'profie': 0}), color=KeyboardButtonColor.POSITIVE)
	).get_json()
	start = (Keyboard(one_time=True)
		.add(Text('Я пассажир &#128519;', payload={'passanger': 1}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Я водитель &#128526;', payload={'driver': 0, 'reg': 0}), color=KeyboardButtonColor.POSITIVE)
	).get_json()
	choose_service = (Keyboard(one_time=False)
		.add(Text('Вызвать такси &#128662;', payload={'taxi': 0}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text('Заказать доставку &#128640;', payload={'delivery': 0}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Моя анкета &#128519;', payload={'user': 0, 'profile': 0}), color=KeyboardButtonColor.SECONDARY)
	).get_json()
	user_profile = (Keyboard(one_time=False)
		.add(Text('Удалить анкету', payload={'user': 0, 'delete': 0}), color=KeyboardButtonColor.NEGATIVE)
		.row()
		.add(Text('Назад', payload={'user': 0, 'back': 0}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text('Написать в техподдержку', payload={'help': 0}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text('Бонусная программа', payload={'promo': 0}), color=KeyboardButtonColor.PRIMARY)
	).get_json()
	driver_profile = (Keyboard(one_time=False)
		.add(Text('Принимать заявки', payload={'driver': 0, 'post_reg': 0}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Удалить анкету', payload={'driver': 0, 'delete': 0}), color=KeyboardButtonColor.NEGATIVE)
		.row()
		.add(Text('Написать в техподдержку', payload={'help': 0}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text('Бонусная программа', payload={'promo': 0}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Пополнить баланс', payload={'give': 0, 'money': 0}), color=KeyboardButtonColor.POSITIVE)
	).get_json()
	payeer = (Keyboard(one_time=False)
		# .add(Text('Пополнить при помощи VK PAY', payload={'driver': 0, 'money': 'vk pay'}), color=KeyboardButtonColor.POSITIVE)
		# .row()
		.add(Text('Пополнить при помощи QIWI', payload={'driver': 0, 'money': 'qiwi'}), color=KeyboardButtonColor.POSITIVE)
		# .row()
	).get_json()
	user_cancel = (Keyboard(one_time=False)
		.add(Text('Назад', payload={'user': 0, 'back': 0}), color=KeyboardButtonColor.NEGATIVE)
	).get_json()
	user_cancel_order = (Keyboard(one_time = False)
		.add(Text('Вызвать повторно', payload={'user': 0, 'return': 0}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Отменить вызов', payload={'user': 0, 'cancel': 0}), color=KeyboardButtonColor.NEGATIVE)
	).get_json()
	driver_order_complete = lambda link, config: (Keyboard(one_time = False)
		.add(Text(f'Буду через {config[0]} минуты!', payload={'driver': 0, 'minute': config[0], 'other': link}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text(f'Буду через {config[1]} минут!', payload={'driver': 0, 'minute': config[1], 'other': link}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text(f'Буду через {config[2]} минут!', payload={'driver': 0, 'minute': config[2], 'other': link}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text('Заказ выполнен &#128526;', payload={'driver': 0, 'success': 0, 'other': link}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Отказаться от заказа', payload={'driver': 0, 'cancel': 0, 'other': link}), color=KeyboardButtonColor.NEGATIVE)
	).get_json()
	vk_pay_keyboard = lambda group_id, amount: (Keyboard(one_time = True)
		.add(VKPay(payload={'driver': 0, 'amount': amount}, hash = f'action=pay-to-group&amount={amount}&group_id={group_id}'))
		.row()
		.add(Text('Назад', payload={'driver': 0, 'profie': 0}), color=KeyboardButtonColor.PRIMARY)
	).get_json()
	starter=Keyboard(one_time = True).add(Text('Начать'), color=KeyboardButtonColor.PRIMARY).get_json()
	location = Keyboard(one_time = True).add(Location(), color=KeyboardButtonColor.PRIMARY).get_json()
	driver_order_complete_will_arrive = lambda link: (Keyboard(one_time = False)
		.add(Text('Выходите', payload={'driver': 0, 'arrived': 0, 'other': link}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text('Заказ выполнен &#128526;', payload={'driver': 0, 'success': 0, 'other': link}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Отказаться от заказа', payload={'driver': 0, 'cancel': 0, 'other': link}), color=KeyboardButtonColor.NEGATIVE)
	).get_json()
	month_no_activity = (Keyboard(one_time = False)
		.add(Text('Вернуться!', payload={'back': 0, 'not user': 0}), color=KeyboardButtonColor.POSITIVE)
	).get_json()
	registration_failed = (Keyboard(one_time = False)
		.add(Text('Продолжить регистрацию', payload={'driver': 0, 'reg': 0}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Удалить анкету', payload={'driver': 0, 'delete': 0}), color=KeyboardButtonColor.NEGATIVE)
	).get_json()
	account_is_off = (Keyboard(one_time=False)
		.add(Text('Включить анкету', payload={'on': 1}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Выйти и удалить анкету', payload={'driver': 0, 'delete': 0}), color=KeyboardButtonColor.NEGATIVE)
	)
	repeat_order = lambda data: (Keyboard()
		.add(Text('Повторить вызов', payload={'repeat': 0, 'data': data}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Назад', payload={'user': 0, 'back': 0}), color=KeyboardButtonColor.PRIMARY)
	).get_json()
	promo = lambda driver: (Keyboard()
		.add(Text('Ввести промокод', payload={'promo': 0, 'insert': 0}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Мой промокод', payload={'promo': 0, 'add': 0}), color=KeyboardButtonColor.PRIMARY)
		.row()
		.add(Text('Назад', payload=({'driver': 0, 'profie': 0} if driver else {'user': 0, 'back': 0})), color=KeyboardButtonColor.NEGATIVE)
	).get_json()
	promo_back = lambda driver: (Keyboard()
		.add(Text('Назад', payload=({'driver': 0, 'profie': 0} if driver else {'user': 0, 'back': 0})), color=KeyboardButtonColor.PRIMARY)
	).get_json()
	pay_bonus = lambda key: (Keyboard()
		.add(Text('Оплатить бонусами', payload=({'passanger': 0, 'pay': 0, 'key': key})), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Не оплачивать бонусами', payload={'user': 0, 'success': 0, 'key': key}), color=KeyboardButtonColor.PRIMARY)
	).get_json()
	driver_arrive_ = lambda link: (Keyboard()
		.add(Text('Заказ выполнен &#128526;', payload={'driver': 0, 'success': 0, 'other': link}), color=KeyboardButtonColor.POSITIVE)
		.row()
		.add(Text('Отказаться от заказа', payload={'driver': 0, 'cancel': 0, 'other': link}), color=KeyboardButtonColor.NEGATIVE)
	).get_json()

	def construct(keyboard_texts:list, keyboard_action:list, payload:list, **kwargs): # Это конструктор клавиатур для людей которые не ссильно разбираются в vkbottle, но которые будт поддерживать этот проект в будущем
		keyboard_object = Keyboard(**kwargs)
		for text, action, payload in zip(keyboard_texts, keyboard_action, payload):
			keyboard_object.add(eval(f'{action}("{text}", payload={payload})')).row()
		return keyboard_object.get_json()