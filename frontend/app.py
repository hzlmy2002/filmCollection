import requests
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
    search_value = request.args.get('search-choice', None, type=str)
    if(search_value):
        if(search_value == 'title'):
            pass
            
        elif(search_value == 'director'):
            pass
        elif(search_value == 'actor'):
            pass
    
    
    movie_pl = table_data.table_data

    #pagination
    global pagination
    pagination.total_data_rows = len(movie_pl) # set this 
    pagination.data_rows_displayed = 50 # set this 
    pagination.start_index = page_num * pagination.data_rows_displayed
    pagination.end_index = pagination.start_index + pagination.data_rows_displayed - 1
    pagination.pages = pagination.total_data_rows // pagination.data_rows_displayed

    print(table_data.genres["all_genres"])
    return render_template('test.html', page=pagination, movies=movie_pl[pagination.start_index:pagination.end_index], genres=table_data.genres["all_genres"])

@app.route('/view-movie-data', methods=['GET'])
def movie_details():
    movie_title = request.args.get('title', 0, type=str)
    movie_details = requests.get('http://' + 'backend:5000' + '/api/v1/searchv2/' + movie_title).json()
    print(movie_details)
    return render_template('movie_detail.html', movie_details=movie_details[0])






if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)
