from time import strftime, gmtime
from aiohttp.web import Application, RouteTableDef, Response, run_app, Request
from aiofiles import open as aiopen
from plugins.database import Database

app = Application()
routes = RouteTableDef()
db = Database()

@routes.get('/styles/style.css')
async def server_get_style(request:Request):
	async with aiopen('table/styles/style.css') as css:
		css_text = await css.read()
	return Response(
		text=css_text,
		content_type='text/css'
	)

@routes.get('/styles/reset.css')
async def server_get_reset(request:Request):
	async with aiopen('table/styles/reset.css') as css:
		css_text = await css.read()
	return Response(
		text=css_text,
		content_type='text/css'
	)

@routes.get('/styles/style.css.map')
async def server_get_map(request:Request):
	async with aiopen('table/styles/style.css.map') as map_:
		map_text = await map_.read()
	return Response(
		text=map_text,
		content_type='text/plain'
	)

@routes.get('/drivers')
async def get_drivers(request:Request):
	async with aiopen('table/drivers.html') as html:
		html_text = await html.read()
	all_drivers = await db.driver.admin_get_all()
	html_text = html_text.replace('{table}', '''<tr>
					{VK}
					{status}
					{gender}
					{city}
					{name}
					{phone}
					{auto}
					{color}
					{state_number}
					{first_activity}
					{last_activity}
					{quantity}
					{balance}
				</tr>''' * (len(all_drivers)))
	counter = 0
	for driver in all_drivers:
		for index in ['VK', 'status', 'gender', 'city', 'name', 'phone', 'auto', 'color', 'state_number', 'first_activity', 'last_activity', 'quantity', 'balance']:
			if index in ['first_activity', 'last_activity']:
				try:html_text = html_text.replace(f'{{{index}}}', f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{strftime("%c", gmtime(float(driver[index])))}</td>', 1)
				except: html_text = html_text.replace(f'{{{index}}}', f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{driver[index]}</td>', 1)
			else:
				html_text = html_text.replace(f'{{{index}}}', f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{driver[index]}</td>', 1)
		counter += 1
	return Response(
		text=html_text,
		content_type='text/html'
	)

@routes.get('/passangers')
async def get_passangers(request:Request):
	async with aiopen('table/passangers.html') as html:
		html_text = await html.read()
	all_drivers = [record async for record in db.passanger.admin_get_all()]
	html_text = html_text.replace('{table}', '''<tr>
					{VK}
					{gender}
					{city}
					{name}
					{phone}
					{quantity}
					{balance}
				</tr>''' * len(all_drivers))
	counter = 0
	for driver in all_drivers:
		for index in ['VK', 'gender', 'city', 'name', 'phone', 'quantity', 'balance']:
			html_text = html_text.replace(f'{{{index}}}', f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{driver[index]}</td>', 1)
		counter += 1
	return Response(
		text=html_text,
		content_type='text/html'
	)

@routes.get('/orders')
async def get_orders(request:Request):
	async with aiopen('cache/forms.json', 'r', encoding='utf-8') as file:
		_json:dict = eval(await file.read())
	async with aiopen('table/orders.html', 'r', encoding='utf-8') as file:
		html = await file.read()
	html = html.replace('{table}', '''<tr>
					{key}
					{from_id}
					{driver_id}
					{active}
					{in_drive}
					{location}
				</tr>''')
	counter = 0
	for key, data in _json.items():
		html = html.replace('{key}',
			f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{key}</td>',
			1
		)
		for index in ['from_id', 'driver_id', 'active', 'in_drive']:
			html = html.replace(f'{{{index}}}',
				f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{data[index]}</td>',
				1
			)

		html = html.replace('{location}',
			f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{", ".join(map(str, data["data"]["location"]))}</td>',
			1
		)
	return Response(
		text=html,
		content_type='text/html'
	)

if __name__ == '__main__':
	app.add_routes(routes)
	run_app(app, host='127.0.0.1', port=80)