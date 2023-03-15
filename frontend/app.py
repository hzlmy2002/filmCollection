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



    #sorting
    sorting_field = request.args.get('sort', None, type=str)
    sorting_asc = request.args.get('order', None, type=str)
    if(sorting_field and sorting_asc):
        query_str = 'http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=' + sorting_asc + "&sorting_field=" + sorting_field
        table_data.table_data = requests.get(query_str).json()
    
    movie_pl = table_data.table_data

    #pagination
    global pagination
    pagination.total_data_rows = len(movie_pl) # set this 
    pagination.data_rows_displayed = 50 # set this 
    pagination.start_index = page_num * pagination.data_rows_displayed
    pagination.end_index = pagination.start_index + pagination.data_rows_displayed - 1
    pagination.pages = pagination.total_data_rows // pagination.data_rows_displayed


    return render_template('test.html', page=pagination, movies=movie_pl[pagination.start_index:pagination.end_index], genres=table_data.genres["all_genres"])

@app.route('/filter', methods=['GET'])
def filter():
    pass



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)
