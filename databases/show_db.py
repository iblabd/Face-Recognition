import mysql.connector
from connector import DB

DB.command.execute("SHOW DATABASES")

print ("Your databases:")
for x in DB.command:
    print(x)