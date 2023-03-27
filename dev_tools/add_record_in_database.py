import sqlite3

from sys import argv

connection = sqlite3.connect('drivers.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

for _id in argv:
	cursor.execute(f'')
	connection.commit()
	print(f'Added {_id}')