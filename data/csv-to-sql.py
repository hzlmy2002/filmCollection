import csv
from datetime import datetime

# helper functions #

def create_table(table_name:str, field_names:list, field_types:list, primary_keys:list):

    drop_table = 'DROP TABLE IF EXISTS `' + table_name +'`;\n'
    create_table = 'CREATE TABLE `' + table_name +'` (\n'
    table = drop_table + create_table
    
    for i in range(len(field_names)):
        field = '\t`' + field_names[i] + '` ' + field_types[i] + ' DEFAULT NULL,\n'
        table = table + field
    
    primary = '\tPRIMARY KEY ('
    for key in primary_keys:
        primary = primary + '`' + key + '`, '
    primary = primary[:-2] + ')\n'
    table = table + primary

    end_bracket = ');\n'
    table = table + end_bracket

    return table

def write_to_table(table_name:str, values:list):

    lock_table = 'LOCK TABLES `' + table_name +'` WRITE;\n'
    insert_table = 'INSERT INTO `' + table_name +'` VALUES\n'
    table = lock_table + insert_table

    for value in values:
        formatted = []
        for field in value:
            if type(field) == datetime:
                formatted.append(("'" + str(field) + "'"))
            elif field == None or field == 'N/A':
                formatted.append("NULL")
            elif type(field) == str and (field.replace('.','',1)).isdigit():
                formatted.append(field)
            elif type(field) == str:
                field = field.replace("'", "\\'")
                formatted.append(("'" + field + "'"))
            else:
                formatted.append(field)
        table = table + '('
        for f in formatted:
            table = table + str(f) + ','
        table = table[:-1] + '),\n'
    table = table[:-2] + ';\n'

    unlock_table = 'UNLOCK TABLES;\n'
    table = table + unlock_table

    return table

# main function #

# data pre-processing

extended_movie_csv = []
with open('csv-files/extendedMovieData.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the header
    for row in reader:
        extended_movie_csv.append(row)

links_csv = []
with open('csv-files/links.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the header
    for row in reader:
        links_csv.append(row)

movies_csv = []
with open('csv-files/movies.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the header
    for row in reader:
        movies_csv.append(row)

ratings_csv = []
with open('csv-files/ratings.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the header
    for row in reader:
        ratings_csv.append(row)

tags_csv = []
with open('csv-files/tags.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the header
    for row in reader:
        tags_csv.append(row)

movies_dict = {}
genreID_dict = {}
directorID_dict = {}
actorID_dict = {}
imdbID_dict = {}

for movie in movies_csv:
    movieID = movie[0]
    title = movie[1]
    genres = movie[2].split('|')

    movie_dict = {movieID: {"title": title, "genres": genres}}
    movies_dict.update(movie_dict)

    for g in genres:
        if g not in genreID_dict:
            genreID_dict.update({g: (len(genreID_dict) + 1)})

for movie in links_csv:
    movieID = movie[0]
    imdbID = movie[1]
    tmdbID = movie[2]

    if movieID in movies_dict:
        movie_dict = {"imdbID": imdbID, "tmdbID": tmdbID}
        movies_dict[movieID].update(movie_dict)

        imdbID_dict.update({imdbID: movieID})

for movie in extended_movie_csv:
    imdbID = movie[0]
    content = movie[1]
    date = None if movie[2] == 'N/A' else datetime.strptime(movie[2],'%d %b %Y')
    director = movie[3]
    leadActors = [actor.strip() for actor in movie[4].split(',')]
    rotten_tomatoes_rating = None if movie[5] == 'N/A' else movie[5][:-1]

    if imdbID in imdbID_dict: # only add additional info to existing movies in movielens dataset
        movieID = imdbID_dict[imdbID]
        movie_dict = {"content": content, "date": date, "director": director, "actors": leadActors, "rotten_tomatoes_rating": rotten_tomatoes_rating}
        movies_dict[movieID].update(movie_dict)

        if director not in directorID_dict:
            directorID_dict.update({director: (len(directorID_dict) + 1)})

        for a in leadActors:
            if a not in actorID_dict:
                actorID_dict.update({a: (len(actorID_dict) + 1)})

user_ratings_values = []
for rate in ratings_csv:
    userID = rate[0]
    movieID = rate[1]
    rating = rate[2]
    timestamp = rate[3]

    if movieID in movies_dict:
        user_ratings_values.append([userID, movieID, timestamp, rating])

user_tags_values = []
for t in tags_csv:
    userID = t[0]
    movieID = t[1]
    tag = t[2]
    timestamp = t[3]

    if movieID in movies_dict:
        user_tags_values.append([userID, movieID, timestamp, tag])

movies_values = []
movie_genres_values = []
movie_director_values = []
movie_actors_values = []
links_values = []
tmdb_link_values = []

for movieID in movies_dict:
    title = movies_dict[movieID]["title"]
    content = movies_dict[movieID]["content"]
    date = movies_dict[movieID]["date"]
    rotten_tomatoes_rating = movies_dict[movieID]["rotten_tomatoes_rating"]
    movies_values.append([movieID, title, content, date, rotten_tomatoes_rating])

    genres = movies_dict[movieID]["genres"]
    for g in genres:
        movie_genres_values.append([movieID, genreID_dict[g]])

    director = movies_dict[movieID]["director"]
    movie_director_values.append([movieID, directorID_dict[director]])

    actors = movies_dict[movieID]["actors"]
    for a in actors:
        movie_actors_values.append([movieID, actorID_dict[a]])

    imdbID = movies_dict[movieID]["imdbID"]
    links_values.append([movieID, imdbID])

    tmdbID = movies_dict[movieID]["tmdbID"]
    tmdb_link_values.append([imdbID, tmdbID])

genres_values = []
for genre in genreID_dict:
    genres_values.append([genreID_dict[genre], genre])

director_values = []
for director in directorID_dict:
    director_values.append([directorID_dict[director], director])

actor_values = []
for actor in actorID_dict:
    actor_values.append([actorID_dict[actor], actor])

print("data pre-processing complete!")

# set up database

db_name = 'films'

sql_lines = []

create_db = 'CREATE DATABASE IF NOT EXISTS `' + db_name +'`;\n'
sql_lines.append(create_db)

use_db = 'USE `' + db_name +'`;\n'
sql_lines.append(use_db)

# create tables TODO foreign key?

movies_table = create_table(
    "Movies",
    ["movieID", "title", "content", "date", "rotten_tomatoes_rating"],
    ["int(11)", "varchar(255)", "varchar(1023)", "datetime", "int(11)"],
    ["movieID"]
)
sql_lines.append(movies_table)

user_ratings_table = create_table(
    "User_ratings",
    ["userID", "movieID", "timestamp", "movielens_rating"],
    ["int(11)", "int(11)", "int(11)", "double"],
    ["userID", "movieID", "timestamp"]
)
sql_lines.append(user_ratings_table)

user_tags_table = create_table(
    "User_tags",
    ["userID", "movieID", "timestamp", "movielens_tag"],
    ["int(11)", "int(11)", "int(11)", "varchar(511)"],
    ["userID", "movieID", "timestamp"]
)
sql_lines.append(user_tags_table)

movie_genres_table = create_table(
    "Movie_Genres",
    ["movieID", "genreID"],
    ["int(11)", "int(11)"],
    ["movieID", "genreID"]
)
sql_lines.append(movie_genres_table)

genres_table = create_table(
    "Genres",
    ["genreID", "genre"],
    ["int(11)", "varchar(255)"],
    ["genreID"]
)
sql_lines.append(genres_table)

movie_director_table = create_table(
    "Movie_Director",
    ["movieID", "directorID"],
    ["int(11)", "int(11)"],
    ["movieID", "directorID"]
)
sql_lines.append(movie_director_table)

directors_table = create_table(
    "Directors",
    ["directorID", "director_name"],
    ["int(11)", "varchar(255)"],
    ["directorID"]
)
sql_lines.append(directors_table)

links_table = create_table(
    "Links",
    ["movieID", "imdbID"],
    ["int(11)", "int(11)"],
    ["movieID"]
)
sql_lines.append(links_table)

tmdb_link_table = create_table(
    "TMDB_link",
    ["imdbID", "tmdbID"],
    ["int(11)", "int(11)"],
    ["imdbID"]
)
sql_lines.append(tmdb_link_table)

movie_actor_table = create_table(
    "Movie_Actors",
    ["movieID", "actorID"],
    ["int(11)", "int(11)"],
    ["movieID", "actorID"]
)
sql_lines.append(movie_actor_table)

actors_table = create_table(
    "Actors",
    ["actorID", "actor_name"],
    ["int(11)", "varchar(255)"],
    ["actorID"]
)
sql_lines.append(actors_table)

print("table creation complete!")

# insert data into tables

write_movies_table = write_to_table("Movies", movies_values)
sql_lines.append(write_movies_table)

write_user_ratings_table = write_to_table("User_ratings", user_ratings_values)
sql_lines.append(write_user_ratings_table)

write_user_tags_table = write_to_table("User_tags", user_tags_values)
sql_lines.append(write_user_tags_table)

write_movie_genres_table = write_to_table("Movie_Genres", movie_genres_values)
sql_lines.append(write_movie_genres_table)

write_genres_table = write_to_table("Genres", genres_values)
sql_lines.append(write_genres_table)

write_movie_director_table = write_to_table("Movie_Director", movie_director_values)
sql_lines.append(write_movie_director_table)

write_director_table = write_to_table("Directors", director_values)
sql_lines.append(write_director_table)

write_links_table = write_to_table("Links", links_values)
sql_lines.append(write_links_table)

write_tmdb_link__table = write_to_table("TMDB_link", tmdb_link_values)
sql_lines.append(write_tmdb_link__table)

write_movie_actors_table = write_to_table("Movie_Actors", movie_actors_values)
sql_lines.append(write_movie_actors_table)

write_actor_table = write_to_table("Actors", actor_values)
sql_lines.append(write_actor_table)

print("table writing complete!")

# write to sql file

f = open(db_name + '.sql', 'w')

for line in sql_lines:
    f.write(line + '\n')

f.close()

print("sql file complete!")
