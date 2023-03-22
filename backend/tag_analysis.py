from sql_executor import SqlExecutor
from flask_restx import Resource


class GetTagsByGenre(Resource):
    def get(self, genre):
        command = ("SELECT User_tags.movielens_tag AS tag_name, COUNT(Genres.genre) AS tag_count "
                   ",COUNT(Genres.genre) * 100.0 / SUM(COUNT(Genres.genre)) OVER() AS percentage "
                   "FROM User_tags "
                   "JOIN Movie_Genres ON User_tags.movieID = Movie_Genres.movieID "
                   "JOIN Genres ON Movie_Genres.genreID = Genres.genreID "
                   "GROUP BY User_tags.movielens_tag, Genres.genre "
                   f"HAVING Genres.genre = \"{genre}\" AND tag_count > 3 "
                   "ORDER BY tag_count DESC;")
        result = SqlExecutor().execute_sql(command)
        result_dict = SqlExecutor().convert_to_dict(
            result, ["tag_name", "count", "percentage"])
        for tag in result_dict:
            tag["percentage"] = float(tag["percentage"])
        return result_dict


class GetTagsByRating(Resource):
    def get(self, rating):
        command = ("SELECT User_tags.movielens_tag AS tag_name, COUNT(User_tags.movielens_tag) AS tag_count "
                   ",COUNT(User_tags.movielens_tag) * 100.0 / SUM(COUNT(User_tags.movielens_tag)) OVER() AS percentage "
                   "FROM User_tags "
                   "LEFT JOIN User_ratings ON User_tags.userID = User_ratings.userID AND User_tags.movieID = User_ratings.movieID "
                   "GROUP BY User_tags.movielens_tag "
                   "HAVING MAX(User_ratings.movielens_rating) - MIN(User_ratings.movielens_rating) <= 1 AND tag_count > 2 "
                   f"AND ROUND(AVG(User_ratings.movielens_rating)) = {rating} "
                   "ORDER BY tag_count DESC;")
        result = SqlExecutor().execute_sql(command)
        result_dict = SqlExecutor().convert_to_dict(
            result, ["tag_name", "count", "percentage"])
        for tag in result_dict:
            tag["percentage"] = float(tag["percentage"])
        return result_dict
