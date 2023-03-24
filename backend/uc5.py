from conn import dbConnection
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from flask_restx import Resource,Api
from flask import Flask
import pickle
from cache import cache

app = Flask(__name__)
api = Api(app)
parser = api.parser()
parser.add_argument('openness', type=float, required=True)
parser.add_argument('agreeableness', type=float, required=True)
parser.add_argument('emotional_stability', type=float, required=True)
parser.add_argument('conscientiousness', type=float, required=True)
parser.add_argument('extraversion', type=float, required=True)
parser.add_argument('rating', type=float, required=True)

class PredictMovieRating(Resource):
    @api.expect(parser)
    @cache.cached(timeout=3600, query_string=True)
    def get(self):
        args=parser.parse_args()
        params=[]
        params.append(args.openness)
        params.append(args.agreeableness)
        params.append(args.emotional_stability)
        params.append(args.conscientiousness)
        params.append(args.extraversion)
        params.append(args.rating)
        pred=Predictor()
        result=pred.predict(params)
        return {"result":result[0]}

class PredictMovieIDRating(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self,movieID):
        dbConnection.reconnect()
        cursor=dbConnection.cursor()
        statm="select Personality_users.openness, Personality_users.agreeableness,Personality_users.emotional_stability , Personality_users.conscientiousness , Personality_users.extraversion, Personality_ratings.rating from Movies, Personality_ratings, Personality_users where Personality_users.userID = Personality_ratings.userID and Movies.movieID=Personality_ratings.movieID and Movies.rotten_tomatoes_rating is not NULL and Movies.movieID=%s"
        cursor.execute(statm,(movieID,))
        result=cursor.fetchall()
        cursor.close()
        if len(result)==0:
            return -1
        ratings=[]
        pred=Predictor()
        for row in result:
            prediction=pred.predict(row)
            ratings.append(prediction[0])
        return sum(ratings)/len(ratings)




class Trainner():
    def __init__(self,dbConnection):
        self.x=[]
        self.y=[]
        self.conn=dbConnection

    def get_data(self):
        self.conn.reconnect()
        cursor=self.conn.cursor()
        statm="select Personality_users.openness, Personality_users.agreeableness,Personality_users.emotional_stability , Personality_users.conscientiousness , Personality_users.extraversion, Personality_ratings.rating , Movies.rotten_tomatoes_rating  from Movies, Personality_ratings, Personality_users where Personality_users.userID = Personality_ratings.userID and Movies.movieID=Personality_ratings.movieID and Movies.rotten_tomatoes_rating is not NULL"
        cursor.execute(statm)
        result=cursor.fetchall()
        cursor.close()
        for row in result:
            self.x.append(row[:6])
            self.y.append(row[6])
        
    def train(self):
        knn=KNeighborsRegressor(n_neighbors=25)
        knn.fit(self.x,self.y)
        
        with open("model.pkl","wb") as file:
            pickle.dump(knn,file)
        

class Predictor():
    def __init__(self,model_path="model.pkl"):
        with open(model_path,"rb") as file:
            self.model=pickle.load(file)
        

    def predict(self,params):
        return self.model.predict([params])


    