from conn import dbConnection
from flask import request
from flask_restx import Resource
import numpy as np
from flask_restx import reqparse
from cache import cache

# constants
RATING_COUNT = 50
HIGH_SCORE = 5
DECIMAL_PLACE = 2
ROW_LIMIT = 15
# trait codes
OPEN_CODE = 0
AGREE_CODE = 1
EMO_CODE = 2
CON_CODE = 3
EXTRA_CODE = 4

# for each personality trait, which films are given the highest/lowest ratings?
class AnalyseTraitToFilmRanking(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self, trait_code:int, highest:int):
        at = AnalyseTrait(dbConnection)
        return at.getFilmRanking(trait_code, highest)

# for each personality trait, what ratings do users usually give (across all films)?
class AnalyseTraitToFilmRatings(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self, trait_code:int):
        at = AnalyseTrait(dbConnection)
        return at.getFilmRatings(trait_code)
    
# for each personality trait, which genres are given the highest/lowest ratings?
class AnalyseTraitToGenreRanking(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self, trait_code:int, highest:int):
        at = AnalyseTrait(dbConnection)
        return at.getGenreRanking(trait_code, highest)

# for a film, which personality trait liked it most?
class AnalyseFilmToTraits(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self, movieID:int):
        at = AnalyseTrait(dbConnection)
        return at.getTraitFilmRanking(movieID)

# for a genre, which personality trait liked/hated it most?
class AnalyseGenreToTraits(Resource):
    @cache.cached(timeout=3600, query_string=True)
    def get(self, genreID:int, highest:int):
        at = AnalyseTrait(dbConnection)
        return at.getTraitGenreRanking(genreID, highest)

# return list of personality traits
class GetAllTraits(Resource):
    def get(self):
        at = AnalyseTrait(dbConnection)
        return at.getAllTraits()

class AnalyseTrait():
    def __init__(self, conn) -> None:
        self.conn = conn
    
    def getFilmRanking(self, trait_code:int, highest:int):
        sql_statm = "SELECT movies.movieID, movies.title, ROUND(p_table.ratings_avg, " + str(DECIMAL_PLACE) + ")"
        sql_statm += " FROM `Movies` AS movies"
        sql_statm += " JOIN ( SELECT p_ratings.movieID, AVG(p_ratings.rating) AS ratings_avg, COUNT(p_ratings.rating) AS ratings_count"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " WHERE p_users." + self.getTraitString(trait_code) + " > " + str(HIGH_SCORE)
        sql_statm += " GROUP BY p_ratings.movieID"
        sql_statm += " HAVING ratings_count > " + str(RATING_COUNT)
        sql_statm += " ) AS p_table ON p_table.movieID = movies.movieID"
        sql_statm += " ORDER BY p_table.ratings_avg " + ("ASC" if highest == 0 else "DESC")
        sql_statm += " LIMIT " + str(ROW_LIMIT) + ";"
        
        cur = self.conn.cursor()
        cur.execute(sql_statm)
        result = cur.fetchall()
        
        result_list = []
        for row in result:
            movieID = row[0]
            title = row[1]
            ratings = row[2]
            row_dict = {"title": title, "ratings": ratings}
            result_list.append(row_dict)
        
        return result_list
    
    def getFilmRatings(self, trait_code:int):
        sql_statm = "SELECT range_table.p_range, (COUNT(range_table.p_range) * 100 / SUM(COUNT(range_table.p_range)) OVER()) AS percentage"
        sql_statm += " FROM ("
        sql_statm += " SELECT p_users.userID, AVG(p_ratings.rating),"
        sql_statm += " CASE"
        sql_statm += " WHEN AVG(p_ratings.rating) < 1 THEN '0-1'"
        sql_statm += " WHEN AVG(p_ratings.rating) < 2 THEN '1-2'"
        sql_statm += " WHEN AVG(p_ratings.rating) < 3 THEN '2-3'"
        sql_statm += " WHEN AVG(p_ratings.rating) < 4 THEN '3-4'"
        sql_statm += " ELSE '4-5'"
        sql_statm += " END AS p_range"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " WHERE p_users." + self.getTraitString(trait_code) + " > " + str(HIGH_SCORE)
        sql_statm += " GROUP BY p_users.userID) AS range_table"
        sql_statm += " GROUP BY range_table.p_range;"

        cur = self.conn.cursor()
        cur.execute(sql_statm)
        result = cur.fetchall()

        result_dict = {}
        for row in result:
            range = row[0]
            percentage = float(round(row[1],DECIMAL_PLACE))
            result_dict[range] = percentage

        return result_dict

    def getGenreRanking(self, trait_code:int, highest:int):
        sql_statm = "SELECT gen.genre, ROUND(gen_avg_table.p_avg_ratings, " + str(DECIMAL_PLACE) + ")"
        sql_statm += " FROM `Genres` AS gen"
        sql_statm += " JOIN ("
        sql_statm += " SELECT mov_gen.genreID AS p_genreID, AVG(p_ratings.rating) AS p_avg_ratings"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " JOIN `Movie_Genres` AS mov_gen ON mov_gen.movieID = p_ratings.movieID"
        sql_statm += " WHERE p_users." + self.getTraitString(trait_code) + " > " + str(HIGH_SCORE)
        sql_statm += " GROUP BY mov_gen.genreID"
        sql_statm += " ) AS gen_avg_table ON p_genreID = gen.genreID"
        sql_statm += " WHERE gen.genre != '(no genres listed)'"
        sql_statm += " ORDER BY gen_avg_table.p_avg_ratings " + ("ASC" if highest == 0 else "DESC") + ";"

        cur = self.conn.cursor()
        cur.execute(sql_statm)
        result = cur.fetchall()

        result_list = []
        for row in result:
            genre = row[0]
            avg = row[1]
            row_dict = {"genre": genre, "avg": avg}
            result_list.append(row_dict)
        
        return result_list
        
    def getTraitFilmRanking(self, movieID:int):
        sql_statm = "SELECT p_avg_table.trait, ROUND(p_avg_table.ratings_avg, " + str(DECIMAL_PLACE) + ")"
        sql_statm += " FROM ("
        sql_statm += " SELECT 'openness' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " WHERE p_users.openness > " + str(HIGH_SCORE)
        sql_statm += " AND p_ratings.movieID = " + str(movieID)
        sql_statm += " UNION"
        sql_statm += " SELECT 'agreeableness' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " WHERE p_users.agreeableness > " + str(HIGH_SCORE)
        sql_statm += " AND p_ratings.movieID = " + str(movieID)
        sql_statm += " UNION"
        sql_statm += " SELECT 'emotional_stability' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " WHERE p_users.emotional_stability > " + str(HIGH_SCORE)
        sql_statm += " AND p_ratings.movieID = " + str(movieID)
        sql_statm += " UNION"
        sql_statm += " SELECT 'conscientiousness' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " WHERE p_users.conscientiousness > " + str(HIGH_SCORE)
        sql_statm += " AND p_ratings.movieID = " + str(movieID)
        sql_statm += " UNION"
        sql_statm += " SELECT 'extraversion' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " WHERE p_users.extraversion > " + str(HIGH_SCORE)
        sql_statm += " AND p_ratings.movieID = " + str(movieID)
        sql_statm += " ) AS p_avg_table"
        sql_statm += " ORDER BY p_avg_table.ratings_avg DESC;"

        cur = self.conn.cursor()
        cur.execute(sql_statm)
        result = cur.fetchall()

        result_list = []
        for row in result:
            trait = row[0]
            avg = row[1]
            row_dict = {"trait": trait, "avg": avg}
            result_list.append(row_dict)
        
        return result_list

    def getTraitGenreRanking(self, genreID:int, highest:int):
        sql_statm = "SELECT p_avg_table.trait, ROUND(p_avg_table.ratings_avg, " + str(DECIMAL_PLACE) + ")"
        sql_statm += " FROM ("
        sql_statm += " SELECT 'openness' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " JOIN `Movie_Genres` AS mov_gen ON mov_gen.movieID = p_ratings.movieID"
        sql_statm += " WHERE p_users.openness > " + str(HIGH_SCORE)
        sql_statm += " AND mov_gen.genreID = " + str(genreID)
        sql_statm += " UNION"
        sql_statm += " SELECT 'agreeableness' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " JOIN `Movie_Genres` AS mov_gen ON mov_gen.movieID = p_ratings.movieID"
        sql_statm += " WHERE p_users.agreeableness > " + str(HIGH_SCORE)
        sql_statm += " AND mov_gen.genreID = " + str(genreID)
        sql_statm += " UNION"
        sql_statm += " SELECT 'emotional_stability' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " JOIN `Movie_Genres` AS mov_gen ON mov_gen.movieID = p_ratings.movieID"
        sql_statm += " WHERE p_users.emotional_stability > " + str(HIGH_SCORE)
        sql_statm += " AND mov_gen.genreID = " + str(genreID)
        sql_statm += " UNION"
        sql_statm += " SELECT 'conscientiousness' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " JOIN `Movie_Genres` AS mov_gen ON mov_gen.movieID = p_ratings.movieID"
        sql_statm += " WHERE p_users.conscientiousness > " + str(HIGH_SCORE)
        sql_statm += " AND mov_gen.genreID = " + str(genreID)
        sql_statm += " UNION"
        sql_statm += " SELECT 'extraversion' AS trait, AVG(p_ratings.rating) AS ratings_avg"
        sql_statm += " FROM `Personality_users` AS p_users"
        sql_statm += " JOIN `Personality_ratings` AS p_ratings ON p_users.userID = p_ratings.userID"
        sql_statm += " JOIN `Movie_Genres` AS mov_gen ON mov_gen.movieID = p_ratings.movieID"
        sql_statm += " WHERE p_users.extraversion > " + str(HIGH_SCORE)
        sql_statm += " AND mov_gen.genreID = " + str(genreID)
        sql_statm += " ) AS p_avg_table"
        sql_statm += " ORDER BY p_avg_table.ratings_avg " + ("ASC" if highest == 0 else "DESC") + ";"

        cur = self.conn.cursor()
        cur.execute(sql_statm)
        result = cur.fetchall()

        result_list = []
        for row in result:
            trait = row[0]
            avg = row[1]
            row_dict = {"trait": trait, "avg": avg}
            result_list.append(row_dict)
        
        return result_list

    def getAllTraits(self):
        traits = []
        traits.append(self.getTraitString(OPEN_CODE))
        traits.append(self.getTraitString(AGREE_CODE))
        traits.append(self.getTraitString(EMO_CODE))
        traits.append(self.getTraitString(CON_CODE))
        traits.append(self.getTraitString(EXTRA_CODE))
        return traits

    def getTraitString(self, trait_code:int):
        if trait_code == OPEN_CODE:
            return "openness"
        elif trait_code == AGREE_CODE:
            return "agreeableness"
        elif trait_code == EMO_CODE:
            return "emotional_stability"
        elif trait_code == CON_CODE:
            return "conscientiousness"
        else: # EXTRA_CODE
            return "extraversion"
