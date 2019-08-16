#!/usr/bin/python -u

import multiprocessing
import sqlite3
import sys
import tempfile

def worker(i, filename, lock):
	conn = sqlite3.connect(filename)
	conn.execute('PRAGMA synchronous = OFF')
	while 1:
		with lock:
			conn.execute('''INSERT INTO "test" VALUES (strftime('%s','now'))''')
			conn.execute('DELETE FROM "test"')
			sys.stdout.write(str(i))
			conn.commit()

def main():
	with tempfile.NamedTemporaryFile() as file:
		print file.name
		conn = sqlite3.connect(file.name)
		conn.execute('CREATE TABLE "test" (number INTEGER)')
		conn.close()

		processes = list()
		lock = multiprocessing.Lock()

		for i in range(8):
			process = multiprocessing.Process(target=worker, args=(i, file.name, lock))
			process.start()
			processes.append(process)

		for process in processes:
			process.join()

	return 0

if __name__ == "__main__":
	sys.exit(main())