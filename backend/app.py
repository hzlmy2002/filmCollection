from conn import dbConnection
from flask import Flask
from flask_restx import Api
from uc12 import ViewTitle, ViewDetails
from visual_browsing import GetAllGenres, GetMovieGenres, GetMoviesData

from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI, analyseRatingGroupGenresAPI

app = Flask(__name__)
api = Api(app)


api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')
api.add_resource(GetAllGenres, '/api/v1/view/all-genres')
api.add_resource(GetMovieGenres, '/api/v1/view/movie-genres/<int:movieID>')
api.add_resource(GetMoviesData, '/api/v1/view/movies-data')

api.add_resource(analyseGeneralRatingAPI, '/api/v1/rating/general/<int:movieID>')
api.add_resource(analyseRatingByGenresAPI, '/api/v1/rating/genres/<int:movieID>/<int:genreID>')
api.add_resource(analyseRatingSameGenresAPI, '/api/v1/rating/samegenres/<int:movieID>')
api.add_resource(analyseRatingGroupGenresAPI, '/api/v1/rating/manygenres/<int:movieID>')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
