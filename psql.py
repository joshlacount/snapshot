import os
import psycopg2

DATABASE = os.environ['PSQL_DATABASE']
USER = os.environ['PSQL_USER']
PASSWORD = os.environ['PSQL_PASSWORD']
HOST = os.environ['PSQL_HOST']
PORT = os.environ['PSQL_PORT']

def get_con():
	return psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)

