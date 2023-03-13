from conn import dbConnection
from flask import Flask
from flask_restx import Api
from uc12 import ViewTitle, ViewDetails
from visual_browsing import GetAllGenres, GetMovieGenres, GetMoviesData

app = Flask(__name__)
api = Api(app)


api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')
api.add_resource(GetAllGenres, '/api/v1/view/all-genres')
api.add_resource(GetMovieGenres, '/api/v1/view/movie-genres/<int:movieID>')
api.add_resource(GetMoviesData, '/api/v1/view/movies-data')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
