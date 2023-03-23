from sql_executor import SqlExecutor
from flask import Flask
from flask_restx import Resource, inputs, Api
from cache import cache
from conn import dbConnection

class Format_result():
    def format_genre(self, result, result_dict):
        genre_str = ""
        count = 0
        for i in range(len(result)):
            row = result[i]
            # genre_str += row[2]
            if(i != len(result)-1):
                next_row = result[i+1]
                if(row[0] == next_row[0]): #format multiple genres
                    if(count == 0):
                        genre_str += row[2]
                    temp = " | " + next_row[2]
                    genre_str += temp
                    count += 1
                else:
                    if(count == 0): #only one genre
                        row_dict = {"Title": row[0], "Date": row[1], "Genre": row[2], "Rotten_tomatoes_rating": row[3]}
                    else:
                        row_dict = {"Title": row[0], "Date": row[1], "Genre": genre_str, "Rotten_tomatoes_rating": row[3]}
                    result_dict.append(row_dict)
                    genre_str = ""
                    count = 0
            else:
                if(count == 0):
                    row_dict = {"Title": row[0], "Date": row[1], "Genre": genre_str, "Rotten_tomatoes_rating": row[3]}
                else:
                    row_dict = {"Title": row[0], "Date": row[1], "Genre": row[2], "Rotten_tomatoes_rating": row[3]}
                result_dict.append(row_dict)


class GetAllGenres(Resource):
    # Get a list of all the genres
    @cache.cached(timeout=3600, query_string=True)
    def get(self):
        payload = {}
        command = ("SELECT Genres.genre FROM Genres")
        result = [row[0] for row in SqlExecutor().execute_sql(command)]
        payload["all_genres"] = result
        return payload


class GetMovieGenres(Resource):
    # Get a list of genres for a movie
    @cache.cached(timeout=3600, query_string=True)
    def get(self, movieID):
        payload = {}
        command = ("SELECT Genres.genre "
                   "FROM Movies, Movie_Genres, Genres "
                   "WHERE Movies.movieID = Movie_Genres.movieID AND Movie_Genres.genreID = Genres.genreID ")
        command += "AND Movies.movieID = %s "
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        cursor.execute(command, (movieID,))
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result


app = Flask(__name__)
api = Api(app)

parser = api.parser()
parser.add_argument('sorting_asc', type=inputs.boolean, required=True)
parser.add_argument('sorting_field', type=str, required=True)
parser.add_argument('start_year', type=int)
parser.add_argument('end_year', type=int)
parser.add_argument('genre', type=str)
parser.add_argument('from_rating', type=int)
parser.add_argument('to_rating', type=int)



class GetMoviesData(Resource):
    # Get details of movies after filtering by date, genre and rating and sorting.
    @api.expect(parser)
    @cache.cached(timeout=3600, query_string=True)
    def get(self):
        args = parser.parse_args()
        params=[]
        command = ("SELECT DISTINCT Movies.movieID, Movies.title, Movies.date, Movies.rotten_tomatoes_rating "
                   "FROM Movies "
                   "LEFT JOIN Movie_Genres ON Movies.movieID = Movie_Genres.movieID "
                   "LEFT JOIN Genres ON Movie_Genres.genreID = Genres.genreID ")
        if args.genre is not None:
            command += f"WHERE Genres.genre = %s "
            params.append(args.genre)
        else:
            command += f"WHERE TRUE "
        if args.start_year is not None:
            command += f"AND year(Movies.date) >= %s "
            params.append(args.start_year)
        if args.end_year is not None:
            command += f"AND year(Movies.date) <= %s "
            params.append(args.end_year)
        if args.from_rating is not None:
            command += f"AND Movies.rotten_tomatoes_rating >= %s "
            params.append(args.from_rating)
        if args.to_rating is not None:
            command += f"AND Movies.rotten_tomatoes_rating <= %s "
            params.append(args.to_rating)
        sorting_mode = 'ASC' if args.sorting_asc else 'DESC'
        sorting_field = args.sorting_field
        if sorting_field not in ["movieID", "title", "content", "date", "rotten_tomatoes_rating"]:
            sorting_field="rotten_tomatoes_rating"
        command += f" ORDER BY {sorting_field} {sorting_mode} "
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        cursor.execute(command,tuple(params))
        result = cursor.fetchall()
        result_dict = SqlExecutor().convert_to_dict(
            result, ["movieID", "title", "date", "rotten_tomatoes_rating"])
        cursor.close()
        for movie in result_dict:
            if movie["date"] is not None:
                movie["date"] = movie["date"].strftime("%m/%d/%Y")
            else:
                movie["date"] = ""
            movie["genres"] = GetMovieGenres().get(movie["movieID"])
        return result_dict



