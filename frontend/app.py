import requests, operator
from flask import Flask, render_template, request, make_response, redirect, url_for

app = Flask(__name__)
# api = Api(app, doc='/api/docs')

class TableLoader:
    def __init__(self):
        self.loaded = False
        self.table_data = None
        self.genres = None



# UI component
class Pagination:
    def __init__(self):
        self.start_index = 0
        self.end_index = 0
        self.total_data_rows = 0
        self.data_rows_displayed = 0
        self.pages = 0

pagination = Pagination()


table_data = TableLoader()


@app.route('/', methods=['GET'])
def index():

    # intial loading
    if(table_data.loaded == False):
        print("getting movie data...")
        table_data.table_data = requests.get('http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=true&sorting_field=title').json()
        print("loaded movie data")
        table_data.loaded = True
        table_data.genres = requests.get('http://' + 'backend:5000' + '/api/v1/view/all-genres').json()

    #print(movie_pl)

    #get arguments from frontend
    page_num = request.args.get('page_num', 0, type=int)

    #genre filter
    genre = request.args.get('filter_genre', None, type=str)
    if(genre):
        table_data.table_data = requests.get('http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=true&sorting_field=title&genre=' + genre).json()

    #date filter 
    year_range = request.args.get('year_range', None, type=str)
    year = request.args.get('year', None, type=str)
    if(year_range and year): # both fields have to present for date filter to work
        query_str = 'http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=true&sorting_field=title'
        if(year_range == "before"):
            query_str = query_str +'&end_year=' + year
        elif(year_range == "after"):
            query_str = query_str + '&start_year=' + year
        elif(year_range == "at_year"):
            query_str = query_str + '&start_year=' + year + '&end_year=' + year
        elif(year_range == "between"):
            start_year = None
            end_year = None
            other_year = request.args.get('year_2', None, type=str)
            if(int(other_year) >= int(year)):
                start_year = year
                end_year = other_year
            else:
                start_year = other_year
                end_year = year
            query_str = query_str + '&end_year=' + end_year + '&start_year=' + start_year
        
        table_data.table_data = requests.get(query_str).json()

    #ratings filter
    rating_range = request.args.get('rating_range', None, type=str)
    rating = request.args.get('rating_1', None, type=str)
    if(rating_range and rating): # both fields have to present for date filter to work
        query_str = 'http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=true&sorting_field=rotten_tomatoes_rating'
        if(year_range == "lower"):
            query_str = query_str +'&to_rating=' + rating
        elif(year_range == "higher"):
            query_str = query_str + '&from_rating=' + rating
        elif(year_range == "at_rating"):
            query_str = query_str + '&to_rating=' + rating + '&from_rating=' + rating
        elif(year_range == "between"):
            start_rating = None
            end_rating = None
            other_rating = request.args.get('rating_2', None, type=str)
            if(int(other_rating) >= int(rating)):
                start_rating = rating
                end_rating = other_rating
            else:
                start_rating = other_rating
                end_rating = rating
            query_str = query_str + '&from_rating=' + start_rating + '&to_rating=' + end_rating
        
        table_data.table_data = requests.get(query_str).json()



    #sorting
    sorting_field = request.args.get('sort', None, type=str)
    sorting_asc = request.args.get('order', None, type=str)
    if(sorting_field and sorting_asc):
        query_str = 'http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=' + sorting_asc + "&sorting_field=" + sorting_field
        table_data.table_data = requests.get(query_str).json()

    #search based on title, director and actor
    search_column = request.args.get('search-choice', None, type=str)
    search_value = request.args.get('search-value', None, type=str)
    if(search_column and search_value):
        query_str = 'http://' + 'backend:5000' + '/api/v1/search/' + search_column + '/' + search_value
        table_data.table_data = requests.get(query_str).json()
    
    
    
    movie_pl = table_data.table_data

    #pagination
    global pagination
    pagination.total_data_rows = len(movie_pl) # set this 
    pagination.data_rows_displayed = 50 # set this 
    pagination.start_index = page_num * pagination.data_rows_displayed
    pagination.end_index = pagination.start_index + pagination.data_rows_displayed - 1
    pagination.pages = pagination.total_data_rows // pagination.data_rows_displayed

    print(table_data.genres["all_genres"])
    return render_template('movie_data_table.html', page=pagination, movies=movie_pl[pagination.start_index:pagination.end_index], genres=table_data.genres["all_genres"])

@app.route('/view-movie-data', methods=['GET'])
def movie_details():
    movieID = request.args.get('movieID', None, type=str)
    movie_details = requests.get('http://' + 'backend:5000' + '/api/v1/searchv2/' + str(movieID)).json()
    print(movie_details)
    return render_template('movie_detail.html', movie_details=movie_details[0])



@app.route('/viewer-analytics', methods=['GET'])
def viewer_analytics():
    movie_id = request.args.get('movieID', None, type=int)
    print("Movie ID", movie_id)


    #scattler plot
    query_str = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/ratings/' + str(movie_id)
    scatter_plot_data = requests.get(query_str).json()

    #pie chart
    #bad ratings
    query_str = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/user-group/' + str(movie_id) + '/1'
    bad_ratings = requests.get(query_str).json()

    #good ratings
    query_str = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/user-group/' + str(movie_id) + '/2'
    good_ratings = requests.get(query_str).json()

    #amazingratings
    query_str = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/user-group/' + str(movie_id) + '/3'
    amazing_ratings = requests.get(query_str).json()

    pie_chart_data = [bad_ratings["num_users"], good_ratings["num_users"], amazing_ratings["num_users"]]

    print("pie chart data", pie_chart_data)

    num_users_rated = bad_ratings["num_users"] + good_ratings["num_users"] + amazing_ratings["num_users"]
    #summary statistics
    #movie title and rotten tomatoes

    #Avg User Rating 
    query_str = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/average-rating/' + str(movie_id)
    sum_stat = requests.get(query_str).json()[0]
    print("Sum stat", sum_stat)
    reaction = None
    if(sum_stat["avg_rating"] < 2):
        reaction = 'Bad'
    elif(sum_stat["avg_rating"] >= 2 and sum_stat["avg_rating"] < 4):
        reaction = 'Good'
    else:
        reaction = 'Amazing'
    
    summary_stats = { "title" : sum_stat['title'],
                     "rotten_tomatoes_rating" : sum_stat['rotten_tomatoes_rating'],
                     "avg_rating" : sum_stat['avg_rating'],
                     "reaction" : reaction,
                     "num_users_rated" : num_users_rated
                    }
    
    user_ratios = { "dislike" : round((bad_ratings["num_users"]/num_users_rated) * 100, 2),
                   "like" : round((good_ratings["num_users"]/num_users_rated) * 100, 2),
                   "amazing" : round((amazing_ratings["num_users"]/num_users_rated) * 100, 2)
                    }
    

    return render_template('viewer_analytics_dashboard.html', movie_id=movie_id, summary_stats=summary_stats, scatter_plot_data=scatter_plot_data, pie_chart_data=pie_chart_data, user_ratios=user_ratios)


def generate_text_stats(genre_data):
    temp = sorted(genre_data, key=operator.itemgetter('ratio'), reverse=True)
    fav_genre = temp[0]["genre"]
    fav_genre_2 = temp[1]["genre"]
    fav_genre_3 = temp[2]["genre"]
    fav_score = temp[0]["avg_rating"]
    worst_genre = temp[-1]["genre"]
    worst_score = temp[-1]["avg_rating"]
    if(fav_genre == "(no genres listed)"):
        fav_genre = temp[1]["genre"]
        fav_score = temp[1]["avg_rating"]
    if(worst_genre == "(no genres listed)"):
        worst_genre = temp[-2]["genre"]
        worst_score = temp[-2]["avg_rating"]
    text = "Viewers in this group like " + fav_genre + ", " + fav_genre_2 + " and " + fav_genre_3 + " movies and dislike " + worst_genre + " movies."
    return text

def generate_rating_stats(rating_history, movie_rating):
    agg_avg_rating_history = sum(rating_history) / len(rating_history)
    agg_avg_movie_rating = sum(movie_rating) / len(movie_rating)
    text = None
    if(agg_avg_rating_history < agg_avg_movie_rating):
        diff = agg_avg_movie_rating - agg_avg_rating_history
        if(diff > 1):
            text = "On average, viewers in this group scored this movie higher by " + str(round(diff,2)) + " than their usual rating"
        else:
            text = "On average, viewers in this group scored this movie very similar to their usual rating, however slightly higher by " + str(round(diff,2)) + " than their usual rating"
    elif(agg_avg_rating_history > agg_avg_movie_rating):
        diff = agg_avg_rating_history - agg_avg_movie_rating
        if(diff > 1):
            text = "On average, viewers in this group scored this movie lower by " + str(round(diff,2)) + " than their usual rating"
        else:
            text = "On average, viewers in this group scored this movie very similar to their usual rating, however slightly lower by " + str(round(diff,2)) + " than their usual rating"
        
    else:
        text = "On average, viewers in this group scored this movie the same as their usual rating"

    return text
    

@app.route('/viewer-group-details', methods=['GET'])
def group_analysis():

    movie_id = request.args.get('movieID', None, type=int)
    print("movieId", movie_id)

    #movie_title = request.args.get('movieTitle', None, type=str)
    #print("movie_title", movie_title)

    # group_percentage = request.args.get('percentage', None, type=int)
    # print("percentage", group_percentage)

    user_group_stats = request.args.get('user_group', None, type=int)
    print("user_group_stats", user_group_stats)
    avg_rating_line_data = None
    movie_rating_line_data = None
    grouping = None
    if(user_group_stats):
        # line graphs
        query_str = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/rating-history/' + str(movie_id) + '/' +  str(user_group_stats)
        print("query str", query_str)
        avg_rating_line_data = requests.get(query_str).json()
        print("avg line data", avg_rating_line_data)
        query_str_2 = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/movie-rating/' + str(movie_id) + '/' +  str(user_group_stats)
        movie_rating_line_data = requests.get(query_str_2).json()
        print("move line data", movie_rating_line_data)
        #get analysis text
        text_graphs = generate_rating_stats(avg_rating_line_data["avg_ratings"], movie_rating_line_data["ratings"])

        #genre table
        query_str = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/genre-rating/' + str(movie_id) + '/' +  str(user_group_stats)
        genre_data = requests.get(query_str).json()
        print("genre bar data", genre_data)
        # get analysis text
        text_table = generate_text_stats(genre_data)
        
        #user label
        if(user_group_stats == 1):
            grouping = 'dislike'
        elif(user_group_stats == 2):
            grouping = "like"
        elif(user_group_stats == 3):
            grouping = "love"
        
        #get title 
        query_str = 'http://' + 'backend:5000' + '/api/v1/viewer-analysis/average-rating/' + str(movie_id)
        movie_title = requests.get(query_str).json()[0]["title"]
    


    return render_template('viewer_group_details.html', movie_id=movie_id, movie_title=movie_title, grouping=grouping, avg_rating_line_data=avg_rating_line_data, movie_rating_line_data=movie_rating_line_data, genre_data=genre_data, text_table=text_table, text_graphs=text_graphs)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)
