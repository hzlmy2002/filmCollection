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

    if(table_data.loaded == False):
        print("getting movie data...")
        table_data.table_data = requests.get('http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=true&sorting_field=title').json()
        print("loaded movie data")
        table_data.loaded = True
        table_data.genres = requests.get('http://' + 'backend:5000' + '/api/v1/view/all-genres')

    movie_pl = table_data.table_data
    #print(movie_pl)

    #get arguments from frontend
    page_num = request.args.get('page_num', 1, type=int)
    # sorting_asc = request.args.get('sorting_asc', 1, type=bool)
    # sorting_field = request.args.get('sorting_field', 1, type=str)
    # genre = request.args.get('genre', 1, type=str)

    #pagination
    global pagination
    pagination.total_data_rows = len(movie_pl) # set this 
    pagination.data_rows_displayed = 50 # set this 
    pagination.start_index = page_num * pagination.data_rows_displayed
    pagination.end_index = pagination.start_index + pagination.data_rows_displayed - 1
    pagination.pages = pagination.total_data_rows // pagination.data_rows_displayed

    return render_template('test.html', page=pagination, movies=movie_pl[pagination.start_index:pagination.end_index], genres=table_data.genres)

@app.route('/filter', methods=['GET'])
def filter():
    pass



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)
