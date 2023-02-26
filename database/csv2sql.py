import MySQLdb
import csv
from datetime import datetime

class CSV2SQL:
    def __init__(self) -> None:
        self.conn=MySQLdb.connect(user="film",password="film",host="localhost",database="films")

    def createTable(self):
        statm1="\
            CREATE TABLE if not exists ratings( \
            user_id int,\
            movie_id int,\
            rating double,\
            timestamp int, \
            PRIMARY KEY (user_id,movie_id) \
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci \
        "
        statm2="\
            CREATE TABLE if not exists movies( \
            movie_id int,\
            title varchar(255),\
            genres varchar(255),\
            PRIMARY KEY (movie_id) \
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci \
        "
        statm3="\
            CREATE TABLE if not exists tags( \
            user_id int,\
            movie_id int,\
            tag varchar(511),\
            timestamp int, \
            PRIMARY KEY (user_id,movie_id,tag) \
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci \
        "
        statm4="\
            CREATE TABLE if not exists links( \
            movie_id int,\
            imdb_id int,\
            tmdb_id int,\
            PRIMARY KEY (movie_id) \
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci \
        "
        statm5="\
            CREATE TABLE if not exists extended_movie_data( \
            imdb_id int,\
            content varchar(1023),\
            date datetime,\
            director varchar(255),\
            lead_actor varchar(255),\
            rotten_tomatoes_score int,\
            PRIMARY KEY (imdb_id) \
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci \
        "

        statm6="\
            CREATE TABLE if not exists similar_tags( \
            tag1 varchar(511),\
            tag2 varchar(511),\
            polarity1 double,\
            polarity2 double,\
            similarity double,\
            PRIMARY KEY (tag1,tag2) \
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci \
        "
        cursor=self.conn.cursor()
        cursor.execute(statm1)
        cursor.execute(statm2)
        cursor.execute(statm3)
        cursor.execute(statm4)
        cursor.execute(statm5)
        cursor.execute(statm6)
        cursor.close()
        self.conn.commit()

    def createIndexes(self):
        statm1="create index ix_ratings on ratings (rating)"
        statm2="create index ix_genres on movies (genres)"
        statm3="create index ix_title on movies (title)"
        statm4="create index ix_tag on tags (tag)"
        statm5="create index ix_imdb_id on links (imdb_id)"
        statm6="create index ix_tmdb_id on links (tmdb_id)"
        statm7="create index ix_rotten_tomatoes_score on extended_movie_data (rotten_tomatoes_score)"

        cursor=self.conn.cursor()
        cursor.execute(statm1)
        cursor.execute(statm2)
        cursor.execute(statm3)
        cursor.execute(statm4)
        cursor.execute(statm5)
        cursor.execute(statm6)
        cursor.execute(statm7)
        cursor.close()
        self.conn.commit()


    def movieDataConverter(self,row):
        if row[2]=="N/A":
            release_time=None
        else:
            release_time=datetime.strptime(row[2],'%d %b %Y')
        rating=row[-1]
        if rating=="N/A":
            rating=0
        else:
            rating=int(rating[:-1])

        return [row[0],row[1],release_time,row[3],row[4],rating]

    def linksPadding(self,row):
        result=[]
        if row[-1].strip()=="":
            result.append(row[0])
            result.append(row[1])
            result.append(None)
            return result
        else:
            return row


    def insertData(self):
        cursor=self.conn.cursor()
        with open("../data/ratings.csv","r") as f:
            reader=csv.reader(f)
            next(reader)
            for row in reader:
                cursor.execute("INSERT INTO ratings VALUES(%s,%s,%s,%s)",row)
        with open("../data/movies.csv","r") as f:
            reader=csv.reader(f)
            next(reader)
            for row in reader:
                cursor.execute("INSERT INTO movies VALUES(%s,%s,%s)",row)
        with open("../data/tags.csv","r") as f:
            reader=csv.reader(f)
            next(reader)
            for row in reader:
                cursor.execute("INSERT INTO tags VALUES(%s,%s,%s,%s)",row)
        with open("../data/links.csv","r") as f:
            reader=csv.reader(f)
            next(reader)
            for row in reader:
                cursor.execute("INSERT INTO links VALUES(%s,%s,%s)",self.linksPadding(row))
        with open("../data/extendedMovieData.csv","r") as f:
            reader=csv.reader(f)
            next(reader)
            for row in reader:
                cursor.execute("INSERT INTO extended_movie_data VALUES(%s,%s,%s,%s,%s,%s)",self.movieDataConverter(row))
        with open("../data/similarTags.csv","r") as f:
            reader=csv.reader(f)
            next(reader)
            for row in reader:
                cursor.execute("INSERT INTO similar_tags VALUES(%s,%s,%s,%s,%s)",row)
        cursor.close()
        self.conn.commit()

    def load_database(self):
        self.createTable()
        self.createIndexes()
        self.insertData()
        self.conn.close()

        

# cq=CSV2SQL()
# cq.run()