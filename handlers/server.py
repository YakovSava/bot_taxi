from sys import argv
from aiohttp.web import Application, RouteTableDef, Response
from .initializer import vk

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
		return Response(text=f'{argv[0]}')

	if reqdata['secret'] == 'ThisISAVerySecretKey':
		await vk.proccess_event(reqdata)
	return Response(text='ok')

app.add_routes(routes)