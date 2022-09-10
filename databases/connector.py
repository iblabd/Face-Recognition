import mysql.connector


class DB:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
    )

    command = connection.cursor()