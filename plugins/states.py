from vkbottle import BaseStateGroup

class PassangerRegState(BaseStateGroup):
	phone = 0
	location = 1
class TaxiState(BaseStateGroup):
	four_quest = 0
class DeliveryState(BaseStateGroup):
	three_quest = 0
class DriverRegState(BaseStateGroup):
	phone = 0
	location = 1
	auto = 2
	color = 3
	state_number = 4
class VkPayPay(BaseStateGroup):
	pay = 0
class QiwiPay(BaseStateGroup):
	pay = 0