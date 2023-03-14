from typing import TypedDict, Tuple
from sql_executor import SqlExecutor
from flask import Flask
from flask_restx import Resource, inputs, Api


# class TableSorting(TypedDict):
#     asc: bool
#     field: str


# class TableFilters(TypedDict):
#     date: Tuple[int, int]
#     genre: str
#     rating: Tuple[float, float]


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


# filters: TableFilters = {
#     'date': (1988, 2000),
#     'genre': 'Action',
#     'rating': (80, 90)
# }
# sorting: TableSorting = {
#     'asc': False,
#     'field': 'title'
# }
# VisualBrowsing().get_films_data(filters, sorting)
