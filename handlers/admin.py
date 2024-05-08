import asyncio

from time import time, strftime, gmtime
from aiohttp import ClientSession
from vkbottle.bot import Message
from plugins.states import Helper
from .initializer import binder, csv, db, dispatcher
from .order import vk

@vk.on.private_message(text = 'admin <commands>')
async def admin_com(message:Message, commands:str):
	if int(message.from_id) in [19714485, 505671804]:
		command = commands.lower().split()
		if command[0] == 'change':
			if command[1].isdigit():
				await binder.set_count(int(command[1]))
				await message.answer(f'Стоимость за одну заявку изменена на {command[1]}')
			else:
				await message.answer('Нужно ввести число!') 
		# elif command[0] == 'histogram':
		# 	await message.answer('Идёт получение данных (надолго!)')
		# 	drivers = [info async for info in db.passanger.get_all_inform()]
		# 	passangers = [info async for info in db.passanger.admin_get_all()]
		# 	csv_for_sort_histogramm, csv_for_histogram, csv_for_histogram_passangers = await asyncio.gather(
		# 		asyncio.create_task(csv.get_csv_for_sort_histogramm([[one['name'], one['VK'], two['quantity']] for one, two in drivers])),
		# 		asyncio.create_task(csv.get_csv_for_histogram([[one['city'], one['name']] for one, two in drivers])),
		# 		asyncio.create_task(csv.get_csv_for_histogram_passanger([[passanger['city'], passanger['name']] for passanger in passangers]))
		# 	)
		# 	all_photo = await asyncio.gather(
		# 		asyncio.create_task(plot.get_sort_histogramm(csv_for_sort_histogramm)),
		# 		asyncio.create_task(plot.get_histogram(csv_for_histogram)),
		# 		asyncio.create_task(plot.get_histogram_passanger(csv_for_histogram_passangers))
		# 	)
		# 	for photo in all_photo:
		# 		document = await PhotoMessageUploader(vk.api).upload(photo, peer_id = message.from_id)
		# 		await message.answer(attachment = document)
		elif command[0] == 'get':
			names = [
				[info async for info in db.passanger.admin_get_all()],
				[info async for info in db.passanger.get_all_inform()]
			]

			csv_files = await csv.get_csv(names)
			async with ClientSession(trust_env=True) as session:
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
					user_id=command[1],
					peer_id=command[1],
					random_id=0,
					message=message.text.split(' ', 2)[-1]
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
		elif command[0] == 'rate':
			await dispatcher.set_rate_file(commands.split(' ', 2)[-1])
			await message.answer('Успешно изменено')
		elif command[0] == 'time':
			await message.answer(f'Серверное время: {strftime("%H:%M:%S", gmtime())}')
		elif command[0] == 'add':
			await dispatcher.add_and_update_drive(time() - (int(command[2])*24*60*60), int(command[1]))
			await message.answer(f'Поездка водителя {command[1]} прошла {command[2]} дней назад')
		elif command[0] == 'force':
			await dispatcher.debug_spec_checker()
			await message.answer('Принуительная проверка завершена')
		elif command[0] == 'stat':
			passangers, drivers = [rec async for rec in db.passanger.admin_get_all()], await db.driver.admin_get_all()
			off_driver_ids = await dispatcher.get_service_file()
			drivers_info = [[driver_id, driver_city] async for driver_id, driver_city in db.driver.get_all() if (driver_id not in off_driver_ids)]
			driver_no_registred_ids = await dispatcher.get_no_registred_drivers()
			aipu = await dispatcher.already_insert_promo_users()
			def map_wrapper(x:list) -> int:
				try: return max(x[1]['3'])
				except: return 0
			orders = list(map(
				map_wrapper,
				list((await dispatcher.get_database_of_times()).items())
			))
			stat = ""
			for _id, _city in drivers_info:
				stat += f"@id{_id} из {_city}\n"
			await message.answer(f'''Статистика
Таблица водителей: http://45.8.230.39:8000/drivers
Таблица пассажиров: http://45.8.230.39:8000/passangers
Количество водителей: {len(drivers)}
Количество водителей: {len(passangers)}
Количество людей получивших промокоды: {len(aipu)} из {len(drivers) + len(passangers)} возможных
Последний заказ был: {strftime('%m.%d %H:%M:%S', gmtime(max(orders)))}
Отключённых аккаунтов: {len(off_driver_ids)}
Недозарегестрированных водителей: {len(driver_no_registred_ids)}
Недозарегестрированные водители: {"@id"+", @id".join(map(str, driver_no_registred_ids))}
Отключённые аккаунты: {"@id"+", @id".join(map(str, off_driver_ids))}
Все доступные водители: {stat}''')
		elif command[0] == 'buttons':
			await binder.set_buttons(list(map(int, command[-1].split('/'))))
		else:
			await message.answer('Неизвестная команда!')

@vk.on.private_message(text='update <passer>')
async def admin_update_database(message:Message, passer:str):
	if int(message.from_id) in [19714485, 505671804]:
		options = passer.lower().split()
		if options[0] == 'passanger':
			if options[1] == 'update':
				if options[4][0] in ['+', '-', '/', '*']:
					try:
						await db.passanger.cursor.execute(f'SELECT * FROM passanger WHERE VK = "{options[2]}"')
						result = await db.passanger.cursor.fetchone()
						result1 = eval(f'{result[options[3]]} {options[4][0]} {options[4][1:]}')
						await db.passanger.cursor.execute(f'UPDATE passanger SET {options[3]} = {result1} WHERE VK = "{options[2]}"')
						await db.passanger.db.commit()
					except Exception as err:
						await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
					else:
						await message.answer('Успешно изменено!')
				else:
					try:
						await db.passanger.cursor.execute(f'UPDATE passanger SET {options[3]} = "{options[4]}" WHERE VK = "{options[2]}"')
						await db.passanger.db.commit()
					except Exception as err:
						await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
					else:
						await message.answer('Успешно изменено!')
			elif options[1] == 'delete':
				try:
					await db.passanger.cursor.execute(f'DELETE FROM passanger WHERE VK = "{options[2]}"')
					await db.passanger.db.commit()
					await dispatcher.force_delete_promo(options[2])
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
						await db.driver.cursor.execute(f'SELECT * FROM driver{num} WHERE VK = "{options[2]}"')
						result = await db.driver.cursor.fetchone()
						result1 = eval(f'{result[options[3]]} {options[4][0]} {options[4][1:]}')
						await db.driver.cursor.execute(f'UPDATE driver{num} SET {options[3]} = {result1} WHERE VK = "{options[2]}"')
						await db.driver.db.commit()
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
						await db.driver.cursor.execute(f'UPDATE driver{num} SET {options[3]} = "{options[4]}" WHERE VK = "{options[2]}"')
						await db.driver.db.commit()
					except Exception as err:
						await message.answer(f'Неизвестная ошибка.\nТрассировка (для разработчика): {str(err)}')
					else:
						await message.answer('Успешно зарегестрировано!')
			elif options[1] == 'delete':
				try:
					await db.driver.cursor.execute(f'DELETE FROM driver WHERE VK = "{options[2]}"')
					await db.driver.db.commit()
					await db.driver.cursor.execute(f'DELETE FROM driver2 WHERE VK = "{options[2]}"')
					await db.driver.db.commit()
					await dispatcher.force_delete_promo(options[2])
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