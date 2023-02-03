import os
from flask import Flask
import csv
from pathlib import Path
import mysql.connector


class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file=None):
        pf = open(password_file, 'r')
        self.connection = mysql.connector.connect(
            user=user, 
            password=pf.read(),
            host=host, # name of the mysql service as set in the docker compose file
            database=database,
            auth_plugin='mysql_native_password'
        )
        pf.close()
        self.cursor = self.connection.cursor()

    # test function
    def populate_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS blog')
        self.cursor.execute('CREATE TABLE blog (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255))')
        self.cursor.executemany('INSERT INTO blog (id, title) VALUES (%s, %s);', [(i, 'Blog post #%d'% i) for i in range (1,5)])
        self.connection.commit()

    # test function
    def query_titles(self):
        self.cursor.execute('SELECT title FROM blog')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec

    #TODO: is this how we load data into database?
    def populate_db_movie_data(self): 
        print("inside populate movie", flush=True)
        csv_movie_data = csv.reader(open("movies.csv")) # TODO: enable path access from data folder
        self.cursor.execute('DROP TABLE IF EXISTS movies')
        print("creating table...")
        self.cursor.execute('CREATE TABLE movies (movieId INT, title VARCHAR(255), genres VARCHAR(255))')
        print("table created")
        for row in csv_movie_data:
            print(row)
            self.cursor.execute('INSERT INTO movies (movieId,title,genres) VALUES(%s,%s,%s)', row)
        self.connection.commit()


server = Flask(__name__)
conn = None

@server.route('/')
def listBlog():
    global conn
    if not conn:
        print("not conn")
        conn = DBManager(password_file='/run/secrets/db-password')
        conn.populate_db()

    print("is conn")
    rec = conn.query_titles()

    response = ''
    for c in rec:
        response = response  + '<div>   Hello  ' + c + '</div>' #test response

    return response



if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0')
