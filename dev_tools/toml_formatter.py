import toml
import json

from os import remove

with open('parameters.json', 'r', encoding='utf-8') as file:
	lines = json.loads(file.read())

remove('parameters.json')

with open('parameters.toml', 'w', encoding='utf-8') as file:
	file.write(toml.dumps(lines))