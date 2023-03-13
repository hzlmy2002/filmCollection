from conn import dbConnection
from flask import Flask, render_template
from flask_restx import Api, Resource
from visual_browsing import VisualBrowsing, TableFilters, TableSorting
from uc12 import ViewTitle, ViewDetails
from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI

app = Flask(__name__)
api = Api(app, doc='/api/docs')
conn = None

#namespace of the API
api_ns = api.namespace('api', description= 'Example')

#add API 
api.add_resource(analyseGeneralRatingAPI, '/api/v1/rating/general/<int:movieID>')
api.add_resource(analyseRatingByGenresAPI, '/api/v1/rating/genres/<int:movieID>/<int:genreID>')
api.add_resource(analyseRatingSameGenresAPI, '/api/v1/rating/samegenres/<int:movieID>')

class DBManager: #TODO: separate file
    def __init__(self):
        self.connection = dbConnection
        self.cursor = self.connection.cursor()
        self.visual_browsing = VisualBrowsing()


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


@api_ns.route('/movies')
class Example(Resource):
    def get(self):
        payload = {'hello': 'world'}
        return payload


#frontend route
@app.route('/movies', methods=['GET']) #TODO: fix this to show at '/' endpoint
def index():
    global conn
    if not conn:
        print("Connecting db...")
        conn = DBManager()
    print("DB is connected")
    print("inside movie table")
    # titles, dates, ratings = conn.query_table_data()
    # data_rows = len(titles)
    filters: TableFilters = {
        'present': False,
        'date': None,
        'genre': None,
        'rating': None
    }
    sorting: TableSorting = {
        'present': False,
        'asc': None,
        'field': None
    }
    movie_pl = conn.visual_browsing.get_films_data(filters, sorting)
    data_rows = len(movie_pl)
    #print(data)

    return render_template('test.html',data_rows=data_rows, movies=movie_pl)


# @app.route('/movies/api/movie_data')
# def movie_data():
#     query = VisualBrowsing

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)