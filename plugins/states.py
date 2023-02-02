from vkbottle import BaseStateGroup


class PassangerRegState(BaseStateGroup):
	phone = 0
	location = 1
	promo = 2


class TaxiState(BaseStateGroup):
	four_quest = 0
	location = 1


class DeliveryState(BaseStateGroup):
	three_quest = 0
	location = 1


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


class Helper(BaseStateGroup):
	question = 0


class PromoState(BaseStateGroup):
	promo = 0