from aiofiles import open as aiopen
from os.path import join

class Csveer:

	def __init__(self):
		pass

	async def get_csv_for_sort_histogramm(self, data:list) -> str:
		string = 'name;vk;trips\n'
		for rec in data:
			string += f'{rec[0]};{rec[1]};{rec[2]}\n'
		return string
	
	# async def get_csv_for_population(self, data:list) -> str:
	# 	string = 'stage;gender;quantity\n'
	# 	for rec in data:
	# 		string += f'{rec[0]};{rec[1]};{rec[2]}\n'
	# 	return string

	async def get_csv_for_tree_diagram(self, data:list) -> str:
		string = 'city;drivers;passangers\n'
		for rec in data:
			string += f'{rec[0]};{rec[1]};{rec[2]}\n'
		return string

	async def get_csv_for_histogram(self, data:list) -> str:
		string = 'city;driver\n'
		for rec in data:
			string += f'{rec[0]};{rec[1]}\n'
		return string

	async def get_csv_for_histogram_passanger(self, data:list) -> str:
		string = 'city;passanger\n'
		for rec in data:
			string += f'{rec[0]};{rec[1]}\n'
		return string

	async def get_csv(self, all_db:list) -> tuple:
		string = 'VK;gender;city;name;phone;quantity;\n'
		for passanger in all_db[0]:
			string += f'{passanger["VK"]};{passanger["gender"]};{passanger["city"]};{passanger["name"]};{passanger["phone"]};{passanger["quantity"]};\n'
		async with aiopen(join('cache', 'passangers.csv'), 'w', encoding = 'utf-8') as new_csv:
			await new_csv.write(string)
		string = 'VK;status;gender;city;name;phone;auto;color;"state number";"first activity";"last activity";quantity;balance\n'
		for ones, twos in all_db[1]:
			string += f'{ones["VK"]};{ones["status"]};{ones["gender"]};{ones["city"]};{ones["name"]};{ones["phone"]};{ones["auto"]};{ones["color"]};{ones["state_number"]};{ones["first_activity"]};{twos["last_activity"]};{twos["quantity"]};{twos["balance"]}'
		async with aiopen(join('cache', 'drivers.csv'), 'w', encoding = 'utf-8') as new_csv:
			await new_csv.write(string)
		return join('cache', 'passangers.csv'), join('cache', 'drivers.csv')