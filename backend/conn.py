import mysql.connector

dbConnection=mysql.connector.connect(user="root",password="film",host="127.0.0.1",database="films",connect_timeout=5)
dbConnection.ping(reconnect=True)