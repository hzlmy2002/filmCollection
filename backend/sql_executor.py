from typing import Tuple, List
from conn import dbConnection


class SqlExecutor():
    def execute_sql(self, command):
        try:
            cursor = dbConnection.cursor(buffered=True)
            cursor.execute(command)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(e)
            result = {'error': 'error'}
        return result

    def convert_to_dict(self, sql_result: List[Tuple], keys: List):
        result_dict = []
        for row in sql_result:
            row_dict = {}
            for i in range(len(row)):
                row_dict[keys[i]] = row[i]
            result_dict.append(row_dict)
        return result_dict
