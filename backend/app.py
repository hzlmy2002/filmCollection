from conn import dbConnection
from flask import Flask, render_template, request, make_response, redirect, url_for

app = Flask(__name__)

from flask_restx import Api, Resource
from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI
from visual_browsing import GetAllGenres, GetMovieGenres, GetMoviesData
from movie_searcher import GetMovieActors, MovieSearcher, MovieSearcherV2

from flask_caching import Cache

from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI, analyseRatingGroupGenresAPI
from uc3_v2 import GetAllUserRatingsForMovie, GetAvgUserRatingForMovie, GetNumUsersFromRatingGroupForSpecificMovie, GetAvgRatingHistoryOfUsersInRatingGroup, GetAvgRatingInDiffGenresOfUsersInRatingGroup

conn = None

api = Api(app)

#namespace of the API
api_ns = api.namespace('api', description= 'Example')

#UC 1 
api.add_resource(GetAllGenres, '/api/v1/view/all-genres')
api.add_resource(GetMovieGenres, '/api/v1/view/movie-genres/<int:movieID>')
api.add_resource(GetMoviesData, '/api/v1/view/movie-data')

#UC 2
api.add_resource(GetMovieActors, '/api/v1/view/movie-actors/<int:movieID>')
api.add_resource(MovieSearcher, '/api/v1/search/<string:column>/<string:value>')
api.add_resource(MovieSearcherV2, '/api/v1/searchv2/<string:movieTitle>')

#UC 3
api.add_resource(analyseGeneralRatingAPI, '/api/v1/rating/general/<int:movieID>')
api.add_resource(analyseRatingByGenresAPI, '/api/v1/rating/genres/<int:movieID>/<int:genreID>')
api.add_resource(analyseRatingSameGenresAPI, '/api/v1/rating/samegenres/<int:movieID>')
api.add_resource(GetAllUserRatingsForMovie, '/api/v1/viewer-analysis/ratings/<int:movieID>')
api.add_resource(GetAvgUserRatingForMovie, '/api/v1/viewer-analysis/average-rating/<int:movieID>')
api.add_resource(GetNumUsersFromRatingGroupForSpecificMovie, '/api/v1/viewer-analysis/user-group/<int:movieID>/<int:group>')
api.add_resource(GetAvgRatingHistoryOfUsersInRatingGroup, '/api/v1/viewer-analysis/rating-history/<int:movieID>/<int:group>')
api.add_resource(GetAvgRatingInDiffGenresOfUsersInRatingGroup, '/api/v1/viewer-analysis/genre-rating/<int:movieID>/<int:group>')






if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
