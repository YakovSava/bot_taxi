class Forms:

	def __init__(self):
		self.all_forms = {}

	async def new_form(self, from_id:int):
		self.all_forms[from_id] = {'from_id': from_id, 'active': True, 'driver_id': 0}

	async def stop_form(self, from_id:int):
		self.all_forms[from_id]['active'] = False

	async def delete_all_form(self):
		self.all_forms = {}

	def get(self, from_id:int) -> dict:
		return self.all_forms[from_id]