from vkbottle.dispatch import ABCRule
from vkbottle.bot import Message

class Order(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'dict({message.payload})')
		try:
			payload['driver'], payload['order']
		except:
			return False
		else:
			return True

class Delivery(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'dict({message.payload})')
		try:
			payload['driver'], payload['delivery']
		except:
			return False
		else:
			return True

class DriverCancel(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'dict({message.payload})')
		try:
			payload['driver'], payload['cancel']
		except:
			return False
		else:
			return True

class DriverSuccess(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'dict({message.payload})')
		try:
			payload['driver'], payload['success']
		except:
			return False
		else:
			return True

class QiwiPayRule(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'dict({message.payload})')
		try:
			payload['driver'], payload['qiwi']
		except:
			return False
		else:
			return True

class WillArriveMinutes(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'dict({message.payload})')
		try:
			payload['driver'], payload['minutes']
		except:
			return False
		else:
			return True

class Arrived(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'dict({message.payload})')
		try:
			payload['driver'], payload['arrived']
		except:
			return False
		else:
			return True