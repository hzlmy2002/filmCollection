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
        else:
            return {'error':'no result'}


class ViewDetails(Resource):
    def get(self,movie_id):
        try:
            cursor = dbConnection.cursor()
            cursor.execute("select movies.title, extended_movie_data.content, extended_movie_data.date, extended_movie_data.director, extended_movie_data.lead_actor, extended_movie_data.rotten_tomatoes_score from movies, extended_movie_data, links where movies.movie_id = links.movie_id and links.imdb_id = extended_movie_data.imdb_id and movies.movie_id = %s",(movie_id,))
            result = cursor.fetchone()
            cursor.close()

        except Exception as e:
            print(e)
            result = {'error': 'error'}

        if result:
            rt={}
            rt['title']=result[0]
            rt['content']=result[1]
            rt['date']=result[2].strftime('%Y.%m')
            rt['director']=result[3]
            rt['lead_actor']=result[4]
            rt['rotten_tomatoes_score']=result[5] if result[5] !=0 else -1

            return rt
        else:
            return {'error':'no result'}