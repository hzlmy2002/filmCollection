from conn import dbConnection
from flask import Flask, render_template
from flask_restx import Api
from uc12 import ViewTitle, ViewDetails

from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI

app = Flask(__name__)
conn = None
api = Api(app)

class DBManager: #TODO: separate file
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

api.add_resource(analyseGeneralRatingAPI, '/api/v1/rating/general/<int:movieID>')
api.add_resource(analyseRatingByGenresAPI, '/api/v1/rating/genres/<int:movieID>/<int:genreID>')
api.add_resource(analyseRatingSameGenresAPI, '/api/v1/rating/samegenres/<int:movieID>')

@app.route("/movies") #TODO: seperate display for swagger API and 
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