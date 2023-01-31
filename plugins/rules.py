from vkbottle.dispatch import ABCRule
from vkbottle.bot import Message

null = None

class Order(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'{message.payload}')
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
		payload = eval(f'{message.payload}')
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
		payload = eval(f'{message.payload}')
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
		payload = eval(f'{message.payload}')
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
		payload = eval(f'{message.payload}')
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
		payload = eval(f'{message.payload}')
		try:
			payload['driver'], payload['minute']
		except:
			return False
		else:
			return True

class Arrived(ABCRule[Message]):
	async def check(self, message:Message) -> bool:
		if message.payload is None:
			return False
		payload = eval(f'{message.payload}')
		try:
			payload['driver'], payload['arrived']
		except:
			return False
		else:
			return True

class VkPayRule(ABCRule[Message]):
	async def check(self, message:Message):
		try:
			payload = eval(f'{message.payload}')
			payload['driver'], payload['amount']
		except:
			return False
		else:
			return True

class OffAccountRule(ABCRule[Message]):
	async def check(self, message:Message):
		return ({'driver': 0, 'off': 0} == eval(f'{message.payload}')) or ({'user': 0, 'off': 0} == eval(f'{message.payload}'))


class DeleteAccount(ABCRule[Message]):
	async def check(self, message:Message):
		payload = eval(f'{message.payload}')
		return (payload == {'driver': 0, 'delete': 0}) or (payload == {'user': 0, 'delete': 0})


class CancelOrder(ABCRule[Message]):
	async def check(self, message:Message):
		payload = eval(f'{message.payload}')
		try:
			payload['passager'], payload['cancel'], payload['taxi']
		except:
			return False
		else:
			return True


class PassangerSuccessOrder(ABCRule[Message]):
	async def check(self, message:Message):
		payload = eval(f'{message.payload}')
		try:
			payload['user'], payload['success']
		except:
			return False
		else:
			return True


class PassangerCancelOrder(ABCRule[Message]):
	async def check(self, message:Message):
		payload = eval(f'{message.payload}')
		try:
			payload['user'], payload['cancel']
		except:
			return False
		else:
			return True
	

class PassangerArrived(ABCRule[Message]):
	async def check(self, message:Message):
		payload = eval(f'{message.payload}')
		try:
			payload['passanger'], payload['arrived']
		except:
			return False
		else:
			return True

class Repeater(ABCRule[Message]):
	async def check(self, message:Message):
		payload = eval(f'{message.payload}')
		try:
			payload['repeat']
		except:
			return False
		else:
			return True