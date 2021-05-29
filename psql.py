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

def get_snapshots(playlist_id, user_id):
	with get_con() as con:
		cur = con.cursor()
		cur.execute("""
			SELECT * FROM snapshot
			WHERE playlist_id = %s AND user_id = %s
			ORDER BY timestamp DESC;""",
			(playlist_id, user_id))
		records = cur.fetchall()
	return records

def get_snapshot_tracks(snapshot_id, user_id):
	with get_con() as con:
		cur = con.cursor()
		cur.execute("""
			SELECT track_ids FROM snapshot
			WHERE snapshot_id = %s AND user_id = %s;""",
			(snapshot_id, user_id))
		records = cur.fetchall()
	if len(records[0]) == 0:
		return None
	return records[0][0]

if __name__ == '__main__':
	print(len(get_snapshot_tracks('MTIwNCw2YmM0ZmE0ZjYxNTI4NDQyOWExYzY4ZmE3ZjhjM2QwMDNjYzAxZDU5', 'raider7820')))
