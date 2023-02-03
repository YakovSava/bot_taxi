from aiohttp.web import Application, RouteTableDef, Response, run_app
from aiofiles import open as aiopen
from handlers import db

app = Application()
routes = RouteTableDef()

@routes.get('/styles/style.css')
async def server_get_style(request):
	async with aiopen('table/styles/style.css') as css:
		css_text = await css.read()
	return Response(
		text=css_text,
		content_type='text/css'
	)

@routes.get('/styles/reset.css')
async def server_get_reset(request):
	async with aiopen('table/styles/reset.css') as css:
		css_text = await css.read()
	return Response(
		text=css_text,
		content_type='text/css'
	)

@routes.get('/styles/style.css.map')
async def server_get_map(request):
	async with aiopen('table/styles/style.css.map') as map_:
		map_text = await map_.read()
	return Response(
		text=map_text,
		content_type='text/plain'
	)

@routes.get('/drivers')
async def get_drivers(request):
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
			html_text = html_text.replace(f'{{{index}}}', f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{driver[index]}</td>', 1)
		counter += 1
	return Response(
		text=html_text,
		content_type='text/html'
	)

@routes.get('/passangers')
async def get_passangers(request):
	async with aiopen('table/passangers.html') as html:
		html_text = await html.read()
	all_drivers = await db.driver.admin_get_all()
	html_text = html_text.replace('{table}', '''<tr>
					{VK}
					{gender}
					{city}
					{name}
					{phone}
					{quantity}
				</tr>''' * (len(all_drivers)))
	counter = 0
	for driver in all_drivers:
		for index in ['VK', 'gender', 'city', 'name', 'phone', 'quantity']:
			html_text = html_text.replace(f'{{{index}}}', f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{driver[index]}</td>', 1)
		counter += 1
	return Response(
		text=html_text,
		content_type='text/html'
	)