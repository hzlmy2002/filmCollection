from conn import dbConnection
from flask import Flask, render_template, request
from flask_restx import Api, Resource
from uc12 import ViewTitle, ViewDetails
from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI
from visual_browsing import GetAllGenres, GetMovieGenres, GetMoviesData
from setup_api import SetupApi
app = Flask(__name__)
# api = Api(app, doc='/api/docs')
conn = None

api = Api(app, doc='/api/docs')

#namespace of the API
api_ns = api.namespace('api', description= 'Example')

#UC 1 and UC 2
api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')
api.add_resource(GetAllGenres, '/api/v1/view/all-genres')
api.add_resource(GetMovieGenres, '/api/v1/view/movie-genres/<int:movieID>')
api.add_resource(GetMoviesData, '/api/v1/view/movies-data')

#UC 3
api.add_resource(analyseGeneralRatingAPI, '/api/v1/rating/general/<int:movieID>')
api.add_resource(analyseRatingByGenresAPI, '/api/v1/rating/genres/<int:movieID>/<int:genreID>')
api.add_resource(analyseRatingSameGenresAPI, '/api/v1/rating/samegenres/<int:movieID>')

class DBManager: #TODO: separate file
    def __init__(self):
        self.connection = dbConnection
        self.cursor = self.connection.cursor()
        #self.visual_browsing = VisualBrowsing()
        self.get_movie_data = GetMoviesData()


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

# UI component
class Pagination:
    def __init__(self):
        self.start_index = 0
        self.end_index = 0
        self.total_data_rows = 0
        self.data_rows_displayed = 0
        self.pages = 0


# @api_ns.route('/movies')
# class Example(Resource):
#     def get(self):
#         payload = {'hello': 'world'}
#         return payload


pagination = Pagination()

#frontend route
@app.route('/movies') #TODO: fix this to show at '/' endpoint
def index():
    global conn
    if not conn:
        print("Connecting db...")
        conn = DBManager()
    print("DB is connected")
    print("inside movie table")
    # titles, dates, ratings = conn.query_table_data()
    # data_rows = len(titles)
    # filters: TableFilters = {
    #     'present': False,
    #     'date': None,
    #     'genre': None,
    #     'rating': None
    # }
    # sorting: TableSorting = {
    #     'present': False,
    #     'asc': None,
    #     'field': None
    # }
    movie_pl = conn.get_movie_data

    page_num = request.args.get('page_num', 1, type=int)
    #pagination
    global pagination
    pagination.total_data_rows = len(movie_pl) # set this 
    pagination.data_rows_displayed = 50 # set this 
    pagination.start_index = page_num * pagination.data_rows_displayed
    pagination.end_index = pagination.start_index + pagination.data_rows_displayed - 1
    pagination.pages = pagination.total_data_rows // pagination.data_rows_displayed

    return render_template('test.html', page=pagination, movies=movie_pl[pagination.start_index:pagination.end_index])

# @app.route('/movies') #TODO: fix this to show at '/' endpoint
# def index():
#     global conn
#     if not conn:
#         print("Connecting db...")
#         conn = DBManager()
#     print("DB is connected")
#     print("inside movie table")
#     return render_template('server_table.html')


# @app.route('/api/movie_data')
# def movie_data():
#     print("inside api data")

#     filters: TableFilters = {
#         'present': False,
#         'date': None,
#         'genre': None,
#         'rating': None
#     }
#     sorting: TableSorting = {
#         'present': False,
#         'asc': None,
#         'field': None
#     }

#     search = request.args.get('search[value]')
#     if search:
#         print("searching...")
#         print(f'%{search}%')

#     movie_pl = conn.visual_browsing.get_films_data(filters, sorting)
#     data_rows = len(movie_pl)

#     # response
#     return {
#         'data': movie_pl,
#         'recordsFiltered': data_rows,
#         'recordsTotal': data_rows,
#         'draw': request.args.get('draw', type=int),
#     }
    

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)
