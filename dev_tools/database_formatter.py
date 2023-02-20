import sqlite3 as sql

from os import remove

connection = sql.connect('passangers.db')
connection.row_factory = sql.Row
cursor = connection.cursor()

sql.execute('SELECT * FROM passanger')
records = sql.fetchall()

del connection
del cursor

remove('passangers.db')

connection = sql.connect('passangers.db')
connection.row_factory = sql.Row
cursor = connection.cursor()

cursor.execute('''CREATE TABLE if not exists passanger (
	VK TEXT,
	gender TEXT,
	city TEXT,
	name TEXT,
	phone TEXT,
	quantity INTEGER,
	balance INTEGER
)''')
connection.commit()

for record in records:
	sql.execute('INSERT INTO passanger VALUES (?,?,?,?,?,?)', (record['VK'], record['gender'], record['city'], record['name'], record['phone'], record['quantity'], 0))
connection.commit()