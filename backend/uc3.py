from conn import dbConnection
from flask_restx import Resource
import numpy as np




class analyseRating():
    def __init__(self,conn) -> None:
        self.conn = conn
        self.friendly_user=[]
        self.unfriendly_user=[]
        self.activeUser=[]
        self.inactiveUser=[]

    def getUserAverageRating(self):
        self.friendly_user.clear()
        self.unfriendly_user.clear()
        statm="select userID, avg(movielens_rating) from User_ratings group by userID"
        cur=self.conn.cursor()
        cur.execute(statm)
        result=cur.fetchall()
        for row in result:
            if row[1]>=4:
                self.friendly_user.append(row[0])
            elif row[1]<=3.5:
                self.unfriendly_user.append(row[0])

    def getUserAverageRatingByGenres(self,genereIDList):
        self.friendly_user.clear()
        self.unfriendly_user.clear()
        tmp=[str(i) for i in genereIDList]
        statm="select User_ratings.userID, avg(User_ratings.movielens_rating) as rating from User_ratings,Movie_Genres where User_ratings.movieID=Movie_Genres.movieID and Movie_Genres.genreID in (%s) group by userID"
        cur=self.conn.cursor()
        cur.execute(statm,(", ".join(tmp),))
        result=cur.fetchall()
        for row in result:
            if row[1]>=4:
                self.friendly_user.append(row[0])
            elif row[1]<=3.5:
                self.unfriendly_user.append(row[0])

    def getUserActivity(self):
        self.activeUser.clear()
        self.inactiveUser.clear()
        statm="select count(userID) from User_ratings group by userID"
        cur=self.conn.cursor()
        cur.execute(statm)
        result=cur.fetchall()
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
        self.getUserAverageRating()
        self.getUserActivity()
        friendly_user_rating=-1
        unfriendly_user_rating=-1
        active_user_rating=-1
        inactive_user_rating=-1

        statm="select avg(movielens_rating) from User_ratings where movieID=%s and userID in (%s)"
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
        if result[0]:
            inactive_user_rating=result[0]
        return {"friendly_user_rating":friendly_user_rating,"unfriendly_user_rating":unfriendly_user_rating,"active_user_rating":active_user_rating,"inactive_user_rating":inactive_user_rating}

    def getUserGenreRating(self,movieID,genreIDList):
        self.getUserAverageRatingByGenres(genreIDList)
        self.getUserActivity()
        friendly_user_rating=-1
        unfriendly_user_rating=-1
        active_user_rating=-1
        inactive_user_rating=-1

        statm="select avg(movielens_rating) from User_ratings where movieID=%s and userID in (%s)"
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
        if result[0]:
            inactive_user_rating=result[0]
        return {"friendly_user_rating":friendly_user_rating,"unfriendly_user_rating":unfriendly_user_rating,"active_user_rating":active_user_rating,"inactive_user_rating":inactive_user_rating}
    

    def getSameGenreRating(self,movieID):
        statm="select genreID from Movie_Genres where movieID=%s"
        cur=self.conn.cursor()
        cur.execute(statm,(movieID,))
        result=cur.fetchall()
        if result:
            result=[row[0] for row in result]
            return self.getUserGenreRating(movieID,result)


ar=analyseRating(dbConnection)
aaa=ar.getSameGenreRating(1)



pass