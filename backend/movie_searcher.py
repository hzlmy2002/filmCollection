from sql_executor import SqlExecutor
from visual_browsing import GetMovieGenres
from flask_restx import Resource


class GetMovieActors(Resource):
    def get(self, movieID):
        command = ("SELECT Actors.actor_name "
                   "FROM Movies, Movie_Actors, Actors "
                   "WHERE Movies.movieID = Movie_Actors.movieID AND Movie_Actors.actorID = Actors.actorID "
                   f"AND Movies.movieID = {movieID}")
        result = [row[0] for row in SqlExecutor().execute_sql(command)]
        return result


class MovieSearcher(Resource):
    def get(self, column, value):
        command = ("SELECT DISTINCT Movies.movieID, Movies.title, Movies.content, Movies.date, Movies.rotten_tomatoes_rating, Directors.director_name "
                   "FROM Movies "
                   "LEFT JOIN Movie_Directors ON Movies.movieID = Movie_Directors.movieID "
                   "LEFT JOIN Directors ON Movie_Directors.directorID = Directors.directorID ")
        if column == "actor_name":
            command += ("LEFT JOIN Movie_Actors ON Movies.movieID = Movie_Actors.movieID "
                        "LEFT JOIN Actors ON Movie_Actors.actorID = Actors.actorID ")
        command += f"WHERE LOWER({column}) LIKE \"%{value.lower()}%\""
        result = SqlExecutor().execute_sql(command)
        result_dict = SqlExecutor().convert_to_dict(
            result, ["movieID", "title", "content", "date", "rotten_tomatoes_rating", "director_name"])
        for movie in result_dict:
            if movie["date"] is not None:
                movie["date"] = movie["date"].strftime("%m/%d/%Y")
            else:
                movie["date"] = ""
            movie["actors"] = GetMovieActors().get(movie["movieID"])
            movie["genres"] = GetMovieGenres().get(movie["movieID"])
        return result_dict
