import mysql.connector

dbConnection=mysql.connector.connect(user="root",password="film",host="db",database="films",connect_timeout=5)
dbConnection.ping(reconnect=True)