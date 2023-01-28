import asyncio

from vkbottle.bot import Bot
from sys import argv, platform
from config import vk_token

if platform in ['linux', 'linux2']:
	from multiprocessing import Process
	from vkbottle.callback import BotCallback
	from aiohttp.web import Application, RouteTableDef, Response, run_app

	app = Application()
	routes = RouteTableDef()

	data = {
		'secret': 'ThisISAVerySecretKey',
		'server': 'http://45.8.230.39/callback',
		'title': 'Test taxi call bot group'
	}

	@routes.get('/')
	async def main_page(request):
		return 'Server run!'

	@routes.get('/callback')
	async def callback_api(request):
		try:
			reqdata = await request.json()
		except:
			return Response(status=503)

		if reqdata['type'] == 'confirmation':
			return Response(text='243a8c8e')

		if reqdata['secret'] == 'ThisISAVerySecretKey':
			await vk.proccess_event(reqdata)
		return Response(text='ok')

	app.add_routes(routes)

	pr = Process(target=run_app, args=(app,))
	pr.start()

	vk = Bot(
		token=vk_token,
		callback=BotCallback(
			url=data['server'],
			secret_key=data['secret'],
			title=data['title']
		)
	)


elif platform in ['win32', 'cygwin', 'msys']:
	try:
		asyncio.set_event_loop(asyncio.WindowsSelectorEventLoopPolicy())
	except:
		pass
	vk = Bot(
		token=vk_token
	)

vk.on.vbml_ignore_case = True