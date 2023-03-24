import csv
from datetime import datetime

# helper functions #

def create_table(table_name:str, field_names:list, field_types:list, primary_keys:list):

    drop_table = 'DROP TABLE IF EXISTS `' + table_name +'`;\n'
    create_table = 'CREATE TABLE `' + table_name +'` (\n'
    table = drop_table + create_table
    
    for i in range(len(field_names)):
        null_bool = ' DEFAULT' if field_names[i] not in primary_keys else ' NOT'
        field = '\t`' + field_names[i] + '` ' + field_types[i] + null_bool + ' NULL,\n'
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

    print("write_to_table:", table_name, "-", len(values), "values")

    i = 0
    for value in values:
        table = table + '(' + ','.join(value) + '),\n'
        i += 1
        if i % 10000 == 0:
            print(i, "/", len(values))
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

person_data_csv = []
with open('csv-files/personality-data.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the header
    for row in reader:
        person_data_csv.append(row)

person_ratings_csv = []
with open('csv-files/personality-ratings.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the header
    for row in reader:
        person_ratings_csv.append(row)

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
    directors = [actor.strip() for actor in movie[3].split(',')]
    leadActors = [actor.strip() for actor in movie[4].split(',')]
    rotten_tomatoes_rating = None if movie[5] == 'N/A' else movie[5][:-1]

    if imdbID in imdbID_dict: # only add additional info to existing movies in movielens dataset
        movieID = imdbID_dict[imdbID]
        movie_dict = {"content": content, "date": date, "directors": directors, "actors": leadActors, "rotten_tomatoes_rating": rotten_tomatoes_rating}
        movies_dict[movieID].update(movie_dict)

        for d in directors:
            if d not in directorID_dict:
                directorID_dict.update({d: (len(directorID_dict) + 1)})

        for a in leadActors:
            if a not in actorID_dict:
                actorID_dict.update({a: (len(actorID_dict) + 1)})

user_ratings_values = []
for rate in ratings_csv:
    userID = rate[0]
    movieID = rate[1]
    rating = rate[2]
    timestamp = rate[3]
    timestamp_format = "NULL" if (timestamp == None or timestamp == 'N/A' or timestamp == '') else ("'" + str(datetime.fromtimestamp(int(timestamp))) + "'")

    if movieID in movies_dict:
        user_ratings_values.append([userID, movieID, timestamp_format, rating])

user_tags_values = []
for t in tags_csv:
    userID = t[0]
    movieID = t[1]
    tag = t[2]
    tag_format = "'" + tag.replace("'", "\\'") + "'"
    timestamp = t[3]
    timestamp_format = "NULL" if (timestamp == None or timestamp == 'N/A' or timestamp == '') else ("'" + str(datetime.fromtimestamp(int(timestamp))) + "'")

    if movieID in movies_dict:
        user_tags_values.append([userID, movieID, timestamp_format, tag_format])

person_data_values = []
person_data_userID = []
for user in person_data_csv:
    userID = user[0].strip()
    userID_format = "'" + userID.replace("'", "\\'") + "'"
    openness = user[1].strip()
    openness_format = "NULL" if (openness == None or openness == 'N/A' or openness == '') else openness
    agreeableness = user[2].strip()
    agreeableness_format = "NULL" if (agreeableness == None or agreeableness == 'N/A' or agreeableness == '') else agreeableness
    emotional_stability = user[3].strip()
    emotional_stability_format = "NULL" if (emotional_stability == None or emotional_stability == 'N/A' or emotional_stability == '') else emotional_stability
    conscientiousness = user[4].strip()
    conscientiousness_format = "NULL" if (conscientiousness == None or conscientiousness == 'N/A' or conscientiousness == '') else conscientiousness
    extraversion = user[5].strip()
    extraversion_format = "NULL" if (extraversion == None or extraversion == 'N/A' or extraversion == '') else extraversion

    if userID not in person_data_userID:
        person_data_userID.append(userID) # personality-data.csv contains duplicate lines
        person_data_values.append([userID_format, openness_format, agreeableness_format, emotional_stability_format, conscientiousness_format, extraversion_format])

person_ratings_values = []
person_ratings_IDs = {} # userID: [movieID]
i = 0
for rate in person_ratings_csv:
    userID = rate[0].strip()
    userID_format = "'" + userID.replace("'", "\\'") + "'"
    movieID = rate[1].strip()
    rating = rate[2].strip()
    rating_format = "NULL" if (rating == None or rating == 'N/A' or rating == '') else rating
    timestamp = rate[3].strip()
    timestamp_format = "NULL" if (timestamp == None or timestamp == 'N/A' or timestamp == '') else ("'" + str(datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S')) + "'")
    
    if (userID in person_data_userID) and (movieID in movies_dict):
        if userID not in person_ratings_IDs:
            person_ratings_IDs[userID] = []
        if (userID in person_ratings_IDs) and (movieID not in person_ratings_IDs[userID]):
            person_ratings_IDs[userID].append(movieID) # personality-ratings.csv contains duplicate lines
            person_ratings_values.append([userID_format, movieID, timestamp_format, rating_format])

    i += 1
    if i % 10000 == 0:
        print(i, "/", len(person_ratings_csv))

movies_values = []
movie_genres_values = []
movie_directors_values = []
movie_actors_values = []
links_values = []
tmdb_link_values = []

for movieID in movies_dict:
    if movies_dict[movieID]["title"][-5:-1].isnumeric():
        title = movies_dict[movieID]["title"][:-7]
    else:
        title = movies_dict[movieID]["title"]
    title_format = "NULL" if (title == None or title == 'N/A' or title == '') else ("'" + title.replace("'", "\\'") + "'")
    content = movies_dict[movieID]["content"]
    content_format = "NULL" if (content == None or content == 'N/A' or content == '') else ("'" + content.replace("'", "\\'") + "'")
    date = movies_dict[movieID]["date"]
    if movies_dict[movieID]["title"][-5:-1].isnumeric():
        date_format = ("'" + movies_dict[movieID]["title"][-5:-1] + "-01-01'") if (date == None or date == 'N/A' or date == '') else ("'" + str(date)[:-9] + "'")
    else:
        date_format = "NULL" if (date == None or date == 'N/A' or date == '') else ("'" + str(date)[:-9] + "'")
    rotten_tomatoes_rating = movies_dict[movieID]["rotten_tomatoes_rating"]
    rotten_tomatoes_rating_format = "NULL" if (rotten_tomatoes_rating == None or rotten_tomatoes_rating == 'N/A' or rotten_tomatoes_rating == '') else rotten_tomatoes_rating
    movies_values.append([movieID, title_format, content_format, date_format, rotten_tomatoes_rating_format])

    genres = movies_dict[movieID]["genres"]
    for g in genres:
        movie_genres_values.append([movieID, str(genreID_dict[g])])

    directors = movies_dict[movieID]["directors"]
    for d in directors:
        movie_directors_values.append([movieID, str(directorID_dict[d])])

    actors = movies_dict[movieID]["actors"]
    for a in actors:
        movie_actors_values.append([movieID, str(actorID_dict[a])])

    imdbID = movies_dict[movieID]["imdbID"]
    imdbID_format = "NULL" if (imdbID == None or imdbID == 'N/A' or imdbID == '') else imdbID
    links_values.append([movieID, imdbID_format])

    tmdbID = movies_dict[movieID]["tmdbID"]
    tmdbID_format = "NULL" if (tmdbID == None or tmdbID == 'N/A' or tmdbID == '') else tmdbID
    tmdb_link_values.append([imdbID, tmdbID_format])

genres_values = []
for genre in genreID_dict:
    genre_format = "NULL" if (genre == None or genre == 'N/A' or genre == '') else ("'" + genre.replace("'", "\\'") + "'")
    genres_values.append([str(genreID_dict[genre]), genre_format])

director_values = []
for director in directorID_dict:
    director_format = "NULL" if (director == None or director == 'N/A' or director == '') else ("'" + director.replace("'", "\\'") + "'")
    director_values.append([str(directorID_dict[director]), director_format])

actor_values = []
for actor in actorID_dict:
    actor_format = "NULL" if (actor == None or actor == 'N/A' or actor == '') else ("'" + actor.replace("'", "\\'") + "'")
    actor_values.append([str(actorID_dict[actor]), actor_format])

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
    ["int(11)", "varchar(255)", "varchar(1023)", "date", "int(11)"],
    ["movieID"]
)
sql_lines.append(movies_table)

user_ratings_table = create_table(
    "User_ratings",
    ["userID", "movieID", "timestamp", "movielens_rating"],
    ["int(11)", "int(11)", "datetime", "double"],
    ["userID", "movieID", "movielens_rating"]
)
sql_lines.append(user_ratings_table)

user_tags_table = create_table(
    "User_tags",
    ["userID", "movieID", "timestamp", "movielens_tag"],
    ["int(11)", "int(11)", "datetime", "varchar(511)"],
    ["userID", "movieID", "movielens_tag"]
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

movie_directors_table = create_table(
    "Movie_Directors",
    ["movieID", "directorID"],
    ["int(11)", "int(11)"],
    ["movieID", "directorID"]
)
sql_lines.append(movie_directors_table)

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

person_data_table = create_table(
    "Personality_users",
    ["userID", "openness", "agreeableness", "emotional_stability", "conscientiousness", "extraversion"],
    ["varchar(255)", "double", "double", "double", "double", "double"],
    ["userID"]
)
sql_lines.append(person_data_table)

person_rating_table = create_table(
    "Personality_ratings",
    ["userID", "movieID", "timestamp", "rating"],
    ["varchar(255)", "int(11)", "datetime", "double"],
    ["userID", "movieID"]
)
sql_lines.append(person_rating_table)

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

write_movie_directors_table = write_to_table("Movie_Directors", movie_directors_values)
sql_lines.append(write_movie_directors_table)

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

write_person_data_table = write_to_table("Personality_users", person_data_values)
sql_lines.append(write_person_data_table)

write_person_rating_table = write_to_table("Personality_ratings", person_ratings_values)
sql_lines.append(write_person_rating_table)

print("table writing complete!")

# write to sql file

f = open('../database/' + db_name + '.sql', 'w')

for line in sql_lines:
    if line == sql_lines[-1]:
        f.write(line)
    else:
        f.write(line + '\n')

f.close()

print("sql file complete!")
