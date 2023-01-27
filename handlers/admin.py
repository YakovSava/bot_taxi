import asyncio

from aiohttp import ClientSession
from vkbottle.bot import BotLabeler, Message
from .initializer import *
from plugins.states import Helper

vk = BotLabeler()
vk.vbml_ignore_case = True

@vk.private_message(text = 'admin <commands>')
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
				document = await PhotoMessageUploader(api).upload(photo, peer_id = message.from_id)
				await message.answer(attachment = document)
		elif command[0] == 'get':
			names = [
				[info async for info in db.passanger.admin_get_all()],
				await db.driver.admin_get_all()
			]

			csv_files = await csv.get_csv(names)
			async with ClientSession(trust_env=True) as session:
				for file in csv_files:
					url = await api.docs.get_messages_upload_server(
						peer_id=message.from_id,
						type='doc'
					)
					async with session.post(url.upload_url, data={'file': open(file, 'rb')}) as resp:
						if resp.status == 200:
							response = await resp.json()
							try:
								data = await api.docs.save(file=response['file'], title='CSV')
								await message.answer('Файл:', attachment=data.doc.url.split('?')[0])
							except KeyError:
								await message.answer(f'Что-то пошлоне так {response["error"]}')
						else:
							page = await resp.read()
							await message.answer(f'Прозошла неизвестная ошибка!\nСтатус: {resp.status}\nОшибка: {page.decode()}')
		elif command[0] == 'answer':
			if command[1].isdigit():
				message_id = await api.messages.send(
					user_id = command[1],
					peer_id = command[1],
					random_id = 1,
					message = command[2]
				)
				await message.answer(f'Вы успешно ответили на вопрос {command[0]}\nЕсли вам не нравится ответ, то пропишите "admin delanswer {command[1]} {message_id}"')
			else:
				await message.answer('ID должен быть цифровой!')
		elif command[0] == 'delanswer':
			await api.messages.delete(
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
			all_chats = await api.messages.get_conversations(
				offset=0,
				count=200,
				filter='all'
			)
			for chat in all_chats.items:
				await api.messages.send(
					user_id=chat.conversation.peer.id,
					peer_id=chat.conversation.peer.id,
					random_id=0,
					message=message.text.split(' ', 2)[2]
				)
		else:
			await message.answer('Неизвестная команда!')

@vk.private_message(text='update <passer>')
async def admin_update_database(message:Message, passer:str):
	parameters = await binder.get_parameters()
	if message.from_id in parameters['admin']:
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

@vk.private_message(text='debug <param>')
async def debug_handler(message:Message, param:str):
	parameters = await binder.get_parameters()
	if message.from_id in parameters['admin']:
		options = param.lower().split()
		if options[0] == 'add':
			await dispatcher.add_and_update_drive(time() - (int(options[2])*24*60*60), int(options[1]))
		elif options[0] == 'force':
			await dispatcher.debug_spec_checker()
			
@vk.private_message(payload={'help': 0})
async def helper(message:Message):
	await vk.state_dispenser.set(message.from_id, Helper.question)
	await message.answer('Опишите здесь то что вас интересует и вам ответят в ближайшее время')

@vk.private_message(state = Helper.question)
async def helper_support(message:Message):
	parameters = await binder.get_parameters()
	await vk.state_dispenser.delete(message.from_id)
	await message.answer('Ваш запрос отправлен в техподдержку')
	for admin_id in parameters['admin']:
		await api.messages.send(
			user_id = admin_id,
			peer_id = admin_id,
			random_id = 0,
			message = f'ID: {message.from_id}\nВопрос: {message.text}\n\nОтветить можно командой "admin answer (ID) (message)"'
	)