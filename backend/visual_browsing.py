from enum import Enum
from typing import TypedDict, Tuple


class TableSorting(TypedDict):
    asc: bool
    field: str


class TableFilters(TypedDict):
    date: Tuple[int, int]
    genre: str
    rating: Tuple[float, float]


class VisualBrowsing():
    # def executeSql(self, command):
    #     try:
    #         cursor = dbConnection.cursor()
    #         cursor.execute(command)
    #         result = cursor.fetchone()
    #         cursor.close()
    #     except Exception as e:
    #         print(e)
    #         result = {'error': 'error'}
    #     return result

    def get_genres(self):
        # Check column name and table name
        command = ("SELECT genre FROM genres")

    def get_films_data(self, filters: TableFilters, sorting: TableSorting):
        command = ("SELECT title,date,rotten_tomatoes_rating "
                   "FROM Movie WHERE ")
        command += f"genre = '{filters['genre']}' "
        date = filters['date']
        rating = filters['rating']
        if date[0] != -1:
            command += f"AND date >= {date[0]} "
        if date[1] != -1:
            command += f"AND date <= {date[1]} "
        if rating[0] != -1:
            command += f"AND rating >= {rating[0]} "
        if rating[1] != -1:
            command += f"AND rating <= {rating[1]} "
        sorting_mode = 'ASC' if sorting['asc'] else 'DESC'
        command += f"ORDER BY {sorting['field']} {sorting_mode} "
        print(command)

filters: TableFilters = {
    'date': (1988, 1988),
    'genre': 'Action',
    'rating': (3.5, 3.5)
}
sorting: TableSorting = {
    'asc': False,
    'field' : 'title'
}
VisualBrowsing().get_films_data(filters, sorting)
