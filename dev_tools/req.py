import asyncio

from aiohttp import ClientSession

async def main():
	async with ClientSession() as session:
		async with session.post('http://45.8.230.39/callback', data='{"type": "confirmation"}') as resp:
			print(await resp.read())

if __name__ == '__main__':
	asyncio.run(main())