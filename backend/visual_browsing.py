from typing import TypedDict, Tuple
from sql_executor import SqlExecutor
from flask import Flask
from flask_restx import Resource, inputs, Api

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
    def get(self):
        command = ("SELECT Genres.genre FROM Genres")
        result = [row[0] for row in SqlExecutor().execute_sql(command)]
        return result


class GetMovieGenres(Resource):
    def get(self, movieID):
        command = ("SELECT Genres.genre "
                   "FROM Movies, Movie_Genres, Genres "
                   "WHERE Movies.movieID = Movie_Genres.movieID AND Movie_Genres.genreID = Genres.genreID ")
        command += f"AND Movies.movieID = \"{movieID}\" "
        result = [row[0] for row in SqlExecutor().execute_sql(command)]
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
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        command = ("SELECT DISTINCT Movies.movieID, Movies.title, Movies.date, Movies.rotten_tomatoes_rating "
                   "FROM Movies "
                   "LEFT JOIN Movie_Genres ON Movies.movieID = Movie_Genres.movieID "
                   "LEFT JOIN Genres ON Movie_Genres.genreID = Genres.genreID ")
        if args.genre is not None:
            command += f"WHERE Genres.genre = '{args.genre}' "
        else:
            command += f"WHERE TRUE "
        if args.start_year is not None:
            command += f"AND year(Movies.date) >= {args.start_year} "
        if args.end_year is not None:
            command += f"AND year(Movies.date) <= {args.end_year} "
        if args.from_rating is not None:
            command += f"AND Movies.rotten_tomatoes_rating >= {args.from_rating} "
        if args.to_rating is not None:
            command += f"AND Movies.rotten_tomatoes_rating <= {args.to_rating} "
        sorting_mode = 'ASC' if args.sorting_asc else 'DESC'
        command += f" ORDER BY {args.sorting_field} {sorting_mode} "

        result = SqlExecutor().execute_sql(command)
        result_dict = SqlExecutor().convert_to_dict(
            result, ["movieID", "title", "date", "genre", "rotten_tomatoes_rating"])
        for movie in result_dict:
            if movie["date"] is not None:
                movie["date"] = movie["date"].strftime("%m/%d/%Y")
            else:
                movie["date"] = ""
            movie["genre"] = GetMovieGenres().get(movie["movieID"])
        return result_dict



