from typing import TypedDict, Tuple
from sql_executor import SqlExecutor


class TableSorting(TypedDict):
    asc: bool
    field: str


class TableFilters(TypedDict):
    date: Tuple[int, int]
    genre: str
    rating: Tuple[float, float]


class VisualBrowsing():
    def __init__(self) -> None:
        self.sql_executor = SqlExecutor()

    def get_all_genres(self):
        command = ("SELECT Genres.genre FROM Genres")
        result = self.sql_executor.execute_sql(command)
        return result

    def get_movie_genres(self, title):
        command = ("SELECT Genres.genre "
                   "FROM Movies, Movie_Genres, Genres "
                   "WHERE Movies.movieID = Movie_Genres.movieID AND Movie_Genres.genreID = Genres.genreID ")
        command += f"AND Movies.title = '{title}' "
        result = self.sql_executor.execute_sql(command)
        return result

    def get_films_data(self, filters: TableFilters, sorting: TableSorting):
        command = ("SELECT Movies.title, Movies.date, Genres.genre, Movies.rotten_tomatoes_rating "
                   "FROM Movies "
                   "RIGHT JOIN Movie_Genres ON Movies.movieID = Movie_Genres.movieID "
                   "LEFT JOIN Genres ON Movie_Genres.genreID = Genres.genreID ")
        command += f"WHERE Genres.genre = '{filters['genre']}' "
        date = filters['date']
        rating = filters['rating']
        if date[0] != -1:
            command += f"AND year(Movies.date) >= {date[0]} "
        if date[1] != -1:
            command += f"AND year(Movies.date) <= {date[1]} "
        if rating[0] != -1:
            command += f"AND Movies.rotten_tomatoes_rating >= {rating[0]} "
        if rating[1] != -1:
            command += f"AND Movies.rotten_tomatoes_rating <= {rating[1]} "
        sorting_mode = 'ASC' if sorting['asc'] else 'DESC'
        command += f"\nORDER BY {sorting['field']} {sorting_mode} "

        result = SqlExecutor().execute_sql(command)
        result_dict = SqlExecutor().convert_to_dict(
            result, ["Title", "Date", "Genre", "Rotten_tomatoes_rating"])
        for movie in result_dict:
            movie["Genre"] = self.get_movie_genres(movie["Title"])
        print(result_dict)
        return result_dict


filters: TableFilters = {
    'date': (1988, 2000),
    'genre': 'Action',
    'rating': (80, 90)
}
sorting: TableSorting = {
    'asc': False,
    'field': 'title'
}
VisualBrowsing().get_films_data(filters, sorting)
