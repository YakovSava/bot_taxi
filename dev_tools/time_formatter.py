import sqlite3 as sql

from time import strptime, mktime

connector = sql.connect('drivers.db')
connector.row_factory = sql.Row
cursor = connector.cursor()

def decoding(string:str) -> float:
	return mktime(strptime(string, '%c'))

def get_table() -> list:
	cursor.execute('SELECT * FROM driver2')
	return cursor.fetchall()

def update_table(vk_id:int, new_string:int) -> None:
	cursor.execute(f'UPDATE driver2 SET last_activity = {new_string} WHERE vk = "{vk_id}"')
	connector.commit()

def main():
	table = get_table()
	for record in table:
		new_string = decoding(record['last_activity'])
		update_table(record['vk'], new_string)

if __name__ == '__main__':
	main()