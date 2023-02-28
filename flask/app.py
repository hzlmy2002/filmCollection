import os
from conn import dbConnection
#from database import csv2sql
from flask import Flask, render_template
from flask_restx import Api
from uc12 import ViewTitle, ViewDetails

class DBManager:
    def __init__(self):
        self.connection = dbConnection
        self.cursor = self.connection.cursor()


    # def populate_db(self):
    #     csv2sql.load_database()
    #     print("Database loaded")


    def query_table_data_title(self):
        self.cursor.execute('SELECT title FROM movies')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec
        

app = Flask(__name__)
#api = Api(app)
conn = None


#api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
#api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')

@app.route("/")
def movieTable():
    global conn
    if not conn:
        print("Connecting db...")
        conn = DBManager()
    print("DB is connected")
    print("inside movie table")
    data = conn.query_table_data_title()
    print(data)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)