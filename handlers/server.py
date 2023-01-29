import asyncio

from vkbottle.bot import Bot
from sys import platform
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
		'title': 'Test taxi call'
	}

	vk = Bot(
		token=vk_token,
		callback=BotCallback(
			url=data['server'],
			secret_key=data['secret'],
			title=data['title']
		)
	)

	@routes.get('/')
	async def main_page(request):
		global confirmation_code, secret_key
		confirmation_code, secret_key = await vk.setup_webhook()
		return Response(text='Server run!')

	@routes.post('/callback')
	async def callback_api(request):
		global confirmation_code, secret_key

		try:
			reqdata = await request.json()
		except:
			return Response(status=503)

		if reqdata['type'] == 'confirmation':
			return Response(text=confirmation_code)

		elif reqdata['secret'] == secret_key:
			await vk.process_event(reqdata)
		return Response(text='ok')

	app.add_routes(routes)

	pr = Process(target=run_app, args=(app,), kwargs={'host': '45.8.230.39', 'port': '80'})
	pr.start()


elif platform in ['win32', 'cygwin', 'msys']:
	try:
		asyncio.set_event_loop(asyncio.WindowsSelectorEventLoopPolicy())
	except:
		pass
	vk = Bot(
		token=vk_token
	)

vk.on.vbml_ignore_case = True