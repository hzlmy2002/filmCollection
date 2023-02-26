import mysql.connector

dbConnection=mysql.connector.connect(user="root",password="film",host="db",database="film",connect_timeout=5)
dbConnection.ping(reconnect=True)