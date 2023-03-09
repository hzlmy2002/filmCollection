from enum import Enum
from typing import TypedDict, Tuple
from conn import dbConnection
import json


class TableSorting(TypedDict):
    asc: bool
    field: str


class TableFilters(TypedDict):
    date: Tuple[int, int]
    genre: str
    rating: Tuple[float, float]


class VisualBrowsing():
    def executeSql(self, command):
        try:
            cursor = dbConnection.cursor(buffered=True)
            cursor.execute(command)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(e)
            result = {'error': 'error'}
        return result

    def get_genres(self):
        # Check column name and table name
        command = ("SELECT genre FROM genres")

    def get_films_data(self, filters: TableFilters, sorting: TableSorting):
        command = ("SELECT Movies.title, Movies.date, Genres.genre, Movies.rotten_tomatoes_rating\n"
                   "FROM Movies\n"
                   "RIGHT JOIN Movie_Genres ON Movies.movieID = Movie_Genres.movieID\n"
                   "LEFT JOIN Genres ON Movie_Genres.genreID = Genres.genreID\n")
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

        result = self.executeSql(command)
        result_dict = []
        for row in result:
            row_dict = {"Title": row[0], "Date": row[1], "Genre": row[2], "Rotten_tomatoes_rating": row[3]}
            result_dict.append(row_dict)
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
