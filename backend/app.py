from flask import Flask
from cache import cache
from flask_restx import Api
from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI, analyseRatingGroupGenresAPI
from uc6 import AnalyseTraitToFilmRanking, AnalyseTraitToFilmRatings, AnalyseTraitToGenreRanking, AnalyseFilmToTraits, AnalyseGenreToTraits, GetAllTraits, AnalyseGenreToTraitRange, AnalyseFilmToTraitRange
from visual_browsing import GetAllGenres, GetMovieGenres, GetMoviesData
from tag_analysis import GetTagsByGenre, GetTagsByRating
from movie_searcher import GetMovieActors, MovieSearcher, MovieSearcherV2

from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI, analyseRatingGroupGenresAPI
from uc5 import PredictMovieRating

api = Api()


def create_app():
    app = Flask(__name__)
    with app.app_context():
        api.init_app(app)
        cache.init_app(app, config={'CACHE_TYPE': 'RedisCache','CACHE_REDIS_HOST': 'redis'})

    return app


# namespace of the API
api_ns = api.namespace('api', description='Example')

# UC 1
api.add_resource(GetAllGenres, '/api/v1/view/all-genres')
api.add_resource(GetMovieGenres, '/api/v1/view/movie-genres/<int:movieID>')
api.add_resource(GetMoviesData, '/api/v1/view/movie-data')

# UC 2
api.add_resource(GetMovieActors, '/api/v1/view/movie-actors/<int:movieID>')
api.add_resource(MovieSearcher, '/api/v1/search/<string:column>/<string:value>')
api.add_resource(MovieSearcherV2, '/api/v1/searchv2/<string:movieTitle>')

# UC 3
api.add_resource(analyseGeneralRatingAPI, '/api/v1/rating/general/<int:movieID>')
api.add_resource(analyseRatingByGenresAPI, '/api/v1/rating/genres/<int:movieID>/<int:genreID>')
api.add_resource(analyseRatingSameGenresAPI, '/api/v1/rating/samegenres/<int:movieID>')

# UC4
api.add_resource(GetTagsByGenre, '/api/v1/tags/genre/<string:genre>')
api.add_resource(GetTagsByRating, '/api/v1/tags/rating/<int:rating>')

# UC5
api.add_resource(PredictMovieRating, '/api/v1/predict')

#UC 6
api.add_resource(AnalyseTraitToFilmRanking, '/api/v1/traits/trait-film-ranking/<int:trait_code>/<int:highest>')
api.add_resource(AnalyseTraitToFilmRatings, '/api/v1/traits/trait-film-ratings/<int:trait_code>')
api.add_resource(AnalyseTraitToGenreRanking, '/api/v1/traits/trait-genre-ranking/<int:trait_code>/<int:highest>')
api.add_resource(AnalyseFilmToTraits, '/api/v1/traits/film-traits-ranking/<int:movieID>')
api.add_resource(AnalyseGenreToTraits, '/api/v1/traits/genre-traits-ranking/<int:genreID>/<int:highest>')
api.add_resource(GetAllTraits, '/api/v1/traits/get-all-traits')
api.add_resource(AnalyseGenreToTraitRange, '/api/v1/traits/genre-trait-range/<int:trait_code>/<int:genreID>')
api.add_resource(AnalyseFilmToTraitRange, '/api/v1/traits/film-trait-range/<int:trait_code>/<int:movieID>')
