from conn import dbConnection
from flask import request
from flask_restx import Resource
import numpy as np
from flask_restx import reqparse
from sql_executor import SqlExecutor

# get all ratings of users for a particular movie in ASC order (to plot scatter plot)
query_1 = 'SELECT Movies.movieID, User_ratings.userID, User_ratings.movielens_rating, User_ratings.timestamp FROM Movies, User_ratings \
                    WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = 2 \
                    ORDER BY User_ratings.movielens_rating ASC'

# get average rating of users for particular movie 
query_2 = 'SELECT Movies.movieID, Movies.title, AVG(User_ratings.movielens_rating) FROM Movies, User_ratings \
                    WHERE Movies.movieID = User_ratings.movieID GROUP BY movieID;'

#get highest and lowest rating given for the movie {get first element and last element of query 1}

# get users based on rating range BAD(<=2), GOOD(2<x<4), VERY GOOD(>=4)
query_3 = 'SELECT Movies.movieID, User_ratings.userID, User_ratings.movielens_rating FROM Movies, User_ratings \
            WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = 2 AND User_ratings.movielens_rating < 2;' 

# based on user ID of users (use IN) within each rating group BAD(<=2), OKAY(2<x<4), GOOD(>=4), get their rating habits 
# rating habits are analysed from:
subquery = 'SELECT User_ratings.userID FROM Movies, User_ratings \
            WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = 2 AND User_ratings.movielens_rating < 3;' 

# 1. The avg rating given by each user [users in this category typically give movies an avg score of _] -> display in bar chart? show also the avg value
query_4 = 'SELECT User_ratings.userID, AVG(User_ratings.movielens_rating) FROM User_ratings \
            WHERE User_ratings.userID IN ({subquery}) \
            GROUP BY User_ratings.userID'


# 2. The number of ratings they have given each genre [users in this category give ratings for these genres]

# 3. The avg rating given in each genre 

# all users to plot graph
class GetAllUserRatingsForMovie(Resource):
    def get(self, movieID):
        command = ('SELECT Movies.movieID, User_ratings.userID, User_ratings.movielens_rating, User_ratings.timestamp FROM Movies, User_ratings \
                    WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = %s \
                    ORDER BY User_ratings.timestamp ASC')
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        cursor.execute(command, (movieID,))
        result = cursor.fetchall()
        result_dict = {"ratings": [row[2] for row in result],
                       "timestamp" : [row[3] for row in result]}
        cursor.close()
        return result_dict

# to show statistic
class GetAvgUserRatingForMovie(Resource):
    def get(self, movieID):
        command = ('SELECT Movies.movieID, Movies.title, ROUND(AVG(User_ratings.movielens_rating),2), Movies.rotten_tomatoes_rating FROM Movies, User_ratings \
                    WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = %s  \
                    GROUP BY movieID;')
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        cursor.execute(command, (movieID,))
        result = cursor.fetchall()
        result_dict = SqlExecutor().convert_to_dict(
            result, ["movieID", "title", "avg_rating", "rotten_tomatoes_rating"])
        cursor.close()
        return result_dict
    
#range = 'bad (1)',good (2)','amazing (3)'
#to plot graph
class GetNumUsersFromRatingGroupForSpecificMovie(Resource):
    def get(self, movieID, group):
        command =  ('SELECT COUNT(User_ratings.userID) FROM Movies, User_ratings \
                        WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = %s ')
        if(group == 1):
            command = command + 'AND User_ratings.movielens_rating < 2'
        elif(group == 2):
            command = command + 'AND User_ratings.movielens_rating >=2 AND User_ratings.movielens_rating <4'
        elif(group == 3):
            command = command + 'AND User_ratings.movielens_rating >=4'
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        cursor.execute(command, (movieID,))
        result = cursor.fetchone()
        result_dict = {"num_users" : result[0]}
        cursor.close()
        return result_dict

# returns each user (might want to get an average)
class GetAvgRatingHistoryOfUsersInRatingGroup(Resource):
    def get(self, movieID, group):
        command = ('SELECT User_ratings.userID, ROUND(AVG(User_ratings.movielens_rating),2) FROM User_ratings \
                    WHERE User_ratings.userID IN ( \
	                    SELECT User_ratings.userID FROM Movies, User_ratings \
	                    WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = %s ')
        if(group == 1):
            command = command + 'AND User_ratings.movielens_rating <= 2)'
        elif(group == 2):
            command = command + 'AND User_ratings.movielens_rating >2 AND User_ratings.movielens_rating <=4)'
        elif(group == 3):
            command = command + 'AND User_ratings.movielens_rating >4)'
        command = command + ' GROUP BY User_ratings.userID;'
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        cursor.execute(command, (movieID,))
        result = cursor.fetchall()
        print("Rating history result", result)
        result_dict = {"avg_ratings": [row[1] for row in result],
                       "userId" : [row[0] for row in result]}
        cursor.close()
        return result_dict
    
class GetRatingForMovieForUsersInRatingGroup(Resource):
    def get(self, movieID, group):
        command = ('SELECT User_ratings.userID, User_ratings.movielens_rating FROM User_ratings \
                    LEFT JOIN Movies on User_ratings.movieID = Movies.movieID \
                    WHERE User_ratings.userID IN ( \
	                    SELECT User_ratings.userID FROM Movies, User_ratings \
	                    WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = %s ')
        if(group == 1):
            command = command + 'AND User_ratings.movielens_rating <= 2)'
        elif(group == 2):
            command = command + 'AND User_ratings.movielens_rating >2 AND User_ratings.movielens_rating <=4)'
        elif(group == 3):
            command = command + 'AND User_ratings.movielens_rating >4)'
        command = command + ' AND Movies.movieID = %s;'
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        cursor.execute(command, (movieID,movieID))
        result = cursor.fetchall()
        print("Rating history result", result)
        result_dict = {"ratings": [row[1] for row in result],
                       "userId" : [row[0] for row in result]}
        cursor.close()
        return result_dict
    
class GetAvgRatingInDiffGenresOfUsersInRatingGroup(Resource):
    def get(self, movieID, group):
        command = ('SELECT ROUND(AVG(User_ratings.movielens_rating),2), Genres.genreID, Genres.genre \
                    FROM User_ratings \
                    LEFT JOIN Movies on User_ratings.movieID = Movies.movieID \
                    LEFT JOIN Movie_Genres on Movies.movieID = Movie_Genres.movieID \
                    LEFT JOIN Genres on Movie_Genres.genreID = Genres.genreID \
                    WHERE User_ratings.userID IN ( \
                        SELECT User_ratings.userID FROM Movies, User_ratings \
                        WHERE Movies.movieID = User_ratings.movieID AND Movies.movieID = %s ')
        if(group == 1):
            command = command + 'AND User_ratings.movielens_rating <= 2)'
        elif(group == 2):
            command = command + 'AND User_ratings.movielens_rating >2 AND User_ratings.movielens_rating <=4)'
        elif(group == 3):
            command = command + 'AND User_ratings.movielens_rating >4)'
        command = command + ' GROUP BY Genres.genreID;'
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        cursor.execute(command, (movieID,))
        result = cursor.fetchall()
        print("Genre rating result", result)
        result_dict = SqlExecutor().convert_to_dict(
            result, ["avg_rating", "genreID", "genre"])
        cursor.close()
        return result_dict
    
    #feature to find top 3 movies of users favourite genre