from flask import Flask
from cache import cache
from flask_restx import Api
from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI
from visual_browsing import GetAllGenres, GetMovieGenres, GetMoviesData
from tag_analysis import GetTagsByGenre, GetTagsByRating
from movie_searcher import GetMovieActors, MovieSearcher, MovieSearcherV2

from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI, analyseRatingGroupGenresAPI

api = Api()


def create_app():
    app = Flask(__name__)
    with app.app_context():
        api.init_app(app)
        cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})

    return app


# namespace of the API
api_ns = api.namespace('api', description='Example')

# UC 1
api.add_resource(GetAllGenres, '/api/v1/view/all-genres')
api.add_resource(GetMovieGenres, '/api/v1/view/movie-genres/<int:movieID>')
api.add_resource(GetMoviesData, '/api/v1/view/movie-data')

# UC 2
api.add_resource(GetMovieActors, '/api/v1/view/movie-actors/<int:movieID>')
api.add_resource(
    MovieSearcher, '/api/v1/search/<string:column>/<string:value>')
api.add_resource(MovieSearcherV2, '/api/v1/searchv2/<string:movieTitle>')

# UC 3
api.add_resource(analyseGeneralRatingAPI,
                 '/api/v1/rating/general/<int:movieID>')
api.add_resource(analyseRatingByGenresAPI,
                 '/api/v1/rating/genres/<int:movieID>/<int:genreID>')
api.add_resource(analyseRatingSameGenresAPI,
                 '/api/v1/rating/samegenres/<int:movieID>')

# UC4
api.add_resource(GetTagsByGenre, '/api/v1/tags/genre/<string:genre>')
api.add_resource(GetTagsByRating, '/api/v1/tags/rating/<int:rating>')
