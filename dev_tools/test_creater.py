import sqlite3
import random
import time

connection = sqlite3.connect('drivers.db')
cursor = connection.cursor()

for _ in range(int(input())):
	cursor.execute('INSERT INTO driver2 VALUES (?,?,?,?)', (f'{random.randint(0, 99999)}', time.strftime('%c', time.gmtime(random.randint(0, round(time.time(), 0)))), 0, 0))
	connection.commit()