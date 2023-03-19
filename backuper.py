from time import sleep
from threading import Thread
from shutil import copy

def _create_backup():
	copy('cache', 'backup')

def main():
	while True:
		th = Thread(target=_create_backup)
		th.start()
		sleep(60*60)

if __name__ == '__main__':
	main()