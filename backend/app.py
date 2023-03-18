from conn import dbConnection
from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_restx import Api, Resource
from uc12 import ViewTitle, ViewDetails
from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI
from visual_browsing import GetAllGenres, GetMovieGenres, GetMoviesData
from movie_searcher import GetMovieActors, MovieSearcher, MovieSearcherV2

from uc3 import analyseGeneralRatingAPI, analyseRatingByGenresAPI, analyseRatingSameGenresAPI, analyseRatingGroupGenresAPI

app = Flask(__name__)

conn = None

api = Api(app, doc='/api/docs')

#namespace of the API
api_ns = api.namespace('api', description= 'Example')

#UC 1 
api.add_resource(ViewTitle, '/api/v1/view/title/<string:keyword>')
api.add_resource(ViewDetails, '/api/v1/view/details/<int:movie_id>')
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






if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
