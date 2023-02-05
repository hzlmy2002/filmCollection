from flask_restx import Resource
from conn import dbConnection


class ViewTitle(Resource):
    def get(self,keyword):
        try:
            cursor = dbConnection.cursor()
            cursor.execute("select movie_id,title,genres from movies where title like %s",(f'%{keyword}%',))
            result = cursor.fetchall()
            cursor.close()

        except Exception as e:
            print(e)
            result = {'error': 'error'}

        if result:
            rt=[]
            for row in result:
                rt.append({'movie_id':row[0],'title':row[1],'genres':row[2]})
            return rt