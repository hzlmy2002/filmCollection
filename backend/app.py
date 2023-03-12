from conn import dbConnection
from flask import Flask, render_template
from flask_restx import Api
from uc12 import ViewTitle, ViewDetails

app = Flask(__name__)
conn = None
#api = Api(app)

class DBManager:
    def __init__(self):
        self.connection = dbConnection
        self.cursor = self.connection.cursor()


    # title, date, genre, ratings
    def query_table_data(self):
        titles = []
        dates = []
        genres = []
        ratings = []

        self.cursor.execute('SELECT title FROM Movies')
        for c in self.cursor:
            titles.append(c[0])
        
        self.cursor.execute('SELECT date FROM Movies')
        for c in self.cursor:
            dates.append(c[0])

        self.cursor.execute('SELECT rotten_tomatoes_rating FROM Movies')
        for c in self.cursor:
            ratings.append(c[0])

        return titles, dates, ratings
    
    def format_genres_to_string(self):
        pass
        

# api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
# api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')

@app.route("/")
def movieTable():
    global conn
    if not conn:
        print("Connecting db...")
        conn = DBManager()
    print("DB is connected")
    print("inside movie table")
    titles, dates, ratings = conn.query_table_data()
    data_rows = len(titles)
    #print(data)

    return render_template('table_copy.html', data_rows=data_rows, titles=titles, dates=dates, ratings=ratings)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)