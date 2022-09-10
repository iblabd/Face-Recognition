import mysql.connector
from connector import DB

DB.command.execute("CREATE DATABASE IF NOT EXISTS db_recog")

print("Database successfully created!")