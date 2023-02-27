import os
from conn import dbConnection
#from database import csv2sql
from flask import Flask, render_template
from flask_restx import Api
from uc12 import ViewTitle, ViewDetails

# class DBManager:
#     def __init__(self):
#         self.connection = dbConnection

#     def populate_db(self):
#         csv2sql.load_database()
#         print("Database loaded")
        

app = Flask(__name__)
#api = Api(app)
conn = None


#api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
#api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')

@app.route("/")
def movieTable():
    # global conn
    # if not conn:
    #     conn = DBManager()
    #     conn.populate_db
    # print("DB is connected")
    print("inside movie table")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)