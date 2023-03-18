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
        print(result_dict)
        for tag in result_dict:
            tag["percentage"] = float(tag["percentage"])
        return result_dict
