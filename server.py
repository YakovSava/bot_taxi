from aiohttp.web import Application, RouteTableDef, Response, run_app
from aiofiles import open as aiopen
from handlers import db

app = Application()
routes = RouteTableDef()

async def set_database():
	async with aiopen('table/index.html') as html:
		html_text = await html.read()
	all_drivers = [info for info in db.driver.get_all_inform()]
	html_text = html_text.replace('{table}', '<tr>\n\
					{VK}\n\
					{status}\n\
					{gender}\n\
					{city}\n\
					{name}\n\
					{phone}\n\
					{auto}\n\
					{color}\n\
					{state number}\n\
					{first activity}\n\
					{last activity}\n\
					{quantity}\n\
					{balance}\n\
				</tr>\n'*len(all_drivers))
	for driver in zip(zip(*all_drivers), ['VK', 'status', 'gender', 'city', 'name', 'phone', 'auto', 'color', 'state_number', 'first_activity', 'last_activity', 'quantity', 'balance']):
		counter = 0
		for info in driver[0]:
			html_text = html_text.replace('{'+f'{driver[1].replace("_", " ")}'+'}', f'<td class="{"tg-pvec" if counter % 2 == 0 else "tg-ku2z"}">{info}</td>', 1)
			counter += 1
	return html_text

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

@routes.get('/drivers')
async def get_drivers(request):
	page = await set_database()
	return Response(
		text=page,
		content_type='text/html'
	)