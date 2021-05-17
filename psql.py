import os
import psycopg2


DATABASE = os.environ['PSQL_DATABASE']
USER = os.environ['PSQL_USER']
PASSWORD = os.environ['PSQL_PASSWORD']
HOST = os.environ['PSQL_HOST']
PORT = os.environ['PSQL_PORT']


def get_con():
	return psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)

def insert_snapshot(snapshot_values):
	with get_con() as con:
		cur = con.cursor()
		cur.execute("""
			INSERT INTO snapshot (snapshot_id, timestamp, name, playlist_id, user_id, track_ids)
			VALUES (%s, %s, %s, %s, %s, %s);""",
			snapshot_values)
		con.commit()

def get_snapshot(snapshot_id, user_id):
	with get_con() as con:
		cur = con.cursor()
		cur.execute("""
			SELECT * FROM snapshot
			WHERE snapshot_id = %s AND user_id = %s;""",
			(snapshot_id, user_id))
		records = cur.fetchall()
	if len(records) > 1:
		print("Duplicate snapshot")
	elif len(records) == 0:
		return None
	return records[0]

if __name__ == '__main__':
	import datetime

	"""snapshot = {
		'snapshot_id': 'abc123',
		'timestamp': datetime.datetime.today(),
		'name': 'test',
		'playlist_id': 'def456',
		'user_id': 'ghi789',
		'track_ids': ['123', '456', '789']
	}
	insert_snapshot(snapshot)"""
	print(get_snapshot('abc123', 'ghi789'))
