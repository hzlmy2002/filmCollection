from conn import dbConnection
from flask import request
from flask_restx import Resource
import numpy as np
from flask_restx import reqparse

# get all ratings of users for a particular movie in ASC order (to plot scatter plot)
query_1 = 'SELECT Movies.movieID, User_ratings.userID, User_ratings.movielens_rating, User_ratings.timestamp FROM Movies, User_ratings \
                    WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = 2 \
                    ORDER BY User_ratings.movielens_rating ASC'

# get average rating of users for particular movie 
query_2 = 'SELECT Movies.movieID, Movies.title, AVG(User_ratings.movielens_rating) FROM Movies, User_ratings \
                    WHERE Movies.movieID = User_ratings.movieID GROUP BY movieID;'

#get highest and lowest rating given for the movie {get first element and last element of query 1}

# get users based on rating range 

