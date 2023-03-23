from conn import dbConnection
from flask_restx import Resource
import numpy as np
from flask_restx import reqparse
from cache import cache


class analyseGeneralRatingAPI(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self,movieID):
        ar=analyseRating(dbConnection)
        return ar.getUserRating(movieID)
    
class analyseRatingByGenresAPI(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self,movieID,genreID):
        ar=analyseRating(dbConnection)
        return ar.getUserGenreRating(movieID,[genreID])
    
class analyseRatingSameGenresAPI(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self,movieID):
        ar=analyseRating(dbConnection)
        return ar.getSameGenreRating(movieID)    
class analyseRatingGroupGenresAPI(Resource):
    def put(self,movieID):
        # put request body: genres=genre1,genre2,genre3
        # e.g. genres=1,2,3,10

        parser = reqparse.RequestParser()
        parser.add_argument('genres', action='split', type=int)
        args=parser.parse_args()
        genresList=args['genres']
        if genresList:
            ar=analyseRating(dbConnection)
            return ar.getUserGenreRating(movieID,genresList)
        else:
            return {"error":"genres not found in request body"},400
            
class analyseRating():
    def __init__(self,conn) -> None:
        self.conn = conn
        self.friendly_user=[]
        self.unfriendly_user=[]
        self.activeUser=[]
        self.inactiveUser=[]

    def getUserType(self):
        self.friendly_user.clear()
        self.unfriendly_user.clear()
        statm="select userID, avg(movielens_rating) from User_ratings group by userID"
        self.conn.reconnect()
        cur=self.conn.cursor()
        cur.execute(statm)
        result=cur.fetchall()
        cur.close()
        for row in result:
            if row[1]>=4:
                self.friendly_user.append(row[0])
            elif row[1]<=3.5:
                self.unfriendly_user.append(row[0])

    def getUserTypeByGenres(self,genereIDList):
        self.friendly_user.clear()
        self.unfriendly_user.clear()
        tmp=[str(i) for i in genereIDList]
        statm="select User_ratings.userID, avg(User_ratings.movielens_rating) as rating from User_ratings,Movie_Genres where User_ratings.movieID=Movie_Genres.movieID and Movie_Genres.genreID in (%s) group by userID"
        self.conn.reconnect()
        cur=self.conn.cursor()
        cur.execute(statm,(", ".join(tmp),))
        result=cur.fetchall()
        cur.close()
        for row in result:
            if row[1]>=4:
                self.friendly_user.append(row[0])
            elif row[1]<=3.5:
                self.unfriendly_user.append(row[0])

    def getUserActivity(self):
        self.activeUser.clear()
        self.inactiveUser.clear()
        statm="select count(userID) from User_ratings group by userID"
        self.conn.reconnect()
        cur=self.conn.cursor()
        cur.execute(statm)
        result=cur.fetchall()
        cur.close()
        result=[row[0] for row in result]
        result.sort()
        lower,upper=np.percentile(result,[25,75])
        for i in range(len(result)):
            rating_number=result[i]
            if rating_number<lower:
                self.inactiveUser.append(i+1)
            elif rating_number>upper:
                self.activeUser.append(i+1)

    def getUserRating(self,movieID):
        self.getUserType()
        self.getUserActivity()
        friendly_user_rating=-1
        unfriendly_user_rating=-1
        active_user_rating=-1
        inactive_user_rating=-1

        statm="select avg(movielens_rating) from User_ratings where movieID=%s and userID in (%s)"
        self.conn.reconnect()
        cur=self.conn.cursor()
        tmp=[str(i) for i in self.friendly_user]
        cur.execute(statm,(movieID,", ".join(tmp)))
        result=cur.fetchone()
        if result[0]:
            friendly_user_rating=result[0]
        tmp=[str(i) for i in self.unfriendly_user]
        cur.execute(statm,(movieID,", ".join(tmp)))
        result=cur.fetchone()
        if result[0]:
            unfriendly_user_rating=result[0]
        tmp=[str(i) for i in self.activeUser]
        cur.execute(statm,(movieID,", ".join(tmp)))
        result=cur.fetchone()
        if result[0]:
            active_user_rating=result[0]
        tmp=[str(i) for i in self.inactiveUser]
        cur.execute(statm,(movieID,", ".join(tmp)))
        result=cur.fetchone()
        cur.close()
        if result[0]:
            inactive_user_rating=result[0]
        return {"friendly_user_rating":friendly_user_rating,"unfriendly_user_rating":unfriendly_user_rating,"active_user_rating":active_user_rating,"inactive_user_rating":inactive_user_rating}

    def getUserGenreRating(self,movieID,genreIDList):
        self.getUserTypeByGenres(genreIDList)
        self.getUserActivity()
        friendly_user_rating=-1
        unfriendly_user_rating=-1
        active_user_rating=-1
        inactive_user_rating=-1

        statm="select avg(movielens_rating) from User_ratings where movieID=%s and userID in (%s)"
        self.conn.reconnect()
        cur=self.conn.cursor()
        tmp=[str(i) for i in self.friendly_user]
        cur.execute(statm,(movieID,", ".join(tmp)))
        result=cur.fetchone()
        if result[0]:
            friendly_user_rating=result[0]
        tmp=[str(i) for i in self.unfriendly_user]
        cur.execute(statm,(movieID,", ".join(tmp)))
        result=cur.fetchone()
        if result[0]:
            unfriendly_user_rating=result[0]
        tmp=[str(i) for i in self.activeUser]
        cur.execute(statm,(movieID,", ".join(tmp)))
        result=cur.fetchone()
        if result[0]:
            active_user_rating=result[0]
        tmp=[str(i) for i in self.inactiveUser]
        cur.execute(statm,(movieID,", ".join(tmp)))
        result=cur.fetchone()
        cur.close()
        if result[0]:
            inactive_user_rating=result[0]
        return {"friendly_user_rating":friendly_user_rating,"unfriendly_user_rating":unfriendly_user_rating,"active_user_rating":active_user_rating,"inactive_user_rating":inactive_user_rating}
    

    def getSameGenreRating(self,movieID):
        statm="select genreID from Movie_Genres where movieID=%s"
        self.conn.reconnect()
        cur=self.conn.cursor()
        cur.execute(statm,(movieID,))
        result=cur.fetchall()
        cur.close()
        if result:
            result=[row[0] for row in result]
            return self.getUserGenreRating(movieID,result)