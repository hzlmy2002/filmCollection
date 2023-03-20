import requests
from flask import Flask, render_template, request, make_response, redirect, url_for
import matplotlib.pyplot as plt
from io import BytesIO
import base64

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
    if (table_data.loaded == False):
        print("getting movie data...")
        table_data.table_data = requests.get(
            'http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=true&sorting_field=title').json()
        print("loaded movie data")
        table_data.loaded = True
        table_data.genres = requests.get(
            'http://' + 'backend:5000' + '/api/v1/view/all-genres').json()

    # print(movie_pl)

    # get arguments from frontend
    page_num = request.args.get('page_num', 0, type=int)

    # genre filter
    genre = request.args.get('filter_genre', None, type=str)
    if (genre):
        table_data.table_data = requests.get(
            'http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=true&sorting_field=title&genre=' + genre).json()

    # date filter
    year_range = request.args.get('year_range', None, type=str)
    year = request.args.get('year', None, type=str)
    if (year_range and year):  # both fields have to present for date filter to work
        query_str = 'http://' + 'backend:5000' + \
            '/api/v1/view/movie-data?sorting_asc=true&sorting_field=title'
        if (year_range == "before"):
            query_str = query_str + '&end_year=' + year
        elif (year_range == "after"):
            query_str = query_str + '&start_year=' + year
        elif (year_range == "at_year"):
            query_str = query_str + '&start_year=' + year + '&end_year=' + year
        elif (year_range == "between"):
            start_year = None
            end_year = None
            other_year = request.args.get('year_2', None, type=str)
            if (int(other_year) >= int(year)):
                start_year = year
                end_year = other_year
            else:
                start_year = other_year
                end_year = year
            query_str = query_str + '&end_year=' + end_year + '&start_year=' + start_year

        table_data.table_data = requests.get(query_str).json()

    # ratings filter
    rating_range = request.args.get('rating_range', None, type=str)
    rating = request.args.get('rating_1', None, type=str)
    if (rating_range and rating):  # both fields have to present for date filter to work
        query_str = 'http://' + 'backend:5000' + \
            '/api/v1/view/movie-data?sorting_asc=true&sorting_field=rotten_tomatoes_rating'
        if (year_range == "lower"):
            query_str = query_str + '&to_rating=' + rating
        elif (year_range == "higher"):
            query_str = query_str + '&from_rating=' + rating
        elif (year_range == "at_rating"):
            query_str = query_str + '&to_rating=' + rating + '&from_rating=' + rating
        elif (year_range == "between"):
            start_rating = None
            end_rating = None
            other_rating = request.args.get('rating_2', None, type=str)
            if (int(other_rating) >= int(rating)):
                start_rating = rating
                end_rating = other_rating
            else:
                start_rating = other_rating
                end_rating = rating
            query_str = query_str + '&from_rating=' + \
                start_rating + '&to_rating=' + end_rating

        table_data.table_data = requests.get(query_str).json()

    # sorting
    sorting_field = request.args.get('sort', None, type=str)
    sorting_asc = request.args.get('order', None, type=str)
    if (sorting_field and sorting_asc):
        query_str = 'http://' + 'backend:5000' + '/api/v1/view/movie-data?sorting_asc=' + \
            sorting_asc + "&sorting_field=" + sorting_field
        table_data.table_data = requests.get(query_str).json()

    movie_pl = table_data.table_data

    # pagination
    global pagination
    pagination.total_data_rows = len(movie_pl)  # set this
    pagination.data_rows_displayed = 50  # set this
    pagination.start_index = page_num * pagination.data_rows_displayed
    pagination.end_index = pagination.start_index + pagination.data_rows_displayed - 1
    pagination.pages = pagination.total_data_rows // pagination.data_rows_displayed

    print(table_data.genres["all_genres"])
    return render_template('test.html', page=pagination, movies=movie_pl[pagination.start_index:pagination.end_index], genres=table_data.genres["all_genres"])


@app.route('/filter', methods=['GET'])
def filter():
    pass


def draw_pie_chart(result):
    labels_num = 20 if len(result) > 20 else len(result)
    labels = []
    values = []
    for i in range(labels_num):
        if i == 19:
            labels.append("Other")
            values.append(100 - sum(values))
        else:
            labels.append(result[i]["tag_name"])
            values.append(result[i]["percentage"])

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.pie(values, labels=labels, autopct='%1.1f%%',
           pctdistance=0.9)
    legend_labels = [f'{l}, {s:1.1f}%' for l, s in zip(labels, values)]
    ax.legend(labels=legend_labels)

    chart = BytesIO()
    plt.savefig(chart, format='png')
    chart.seek(0)

    return base64.b64encode(chart.getvalue()).decode('utf-8')


@app.route('/tag-analysis', methods=['GET', 'POST'])
def tag_analysis():
    data = requests.get('http://backend:5000/api/v1/view/all-genres').json()
    if request.method == 'POST':
        analyse_by = request.form.get('analyse_by')
        analyse_options = request.form.get('analyse_options')
        url = f'http://backend:5000/api/v1/tags/{analyse_by}/{analyse_options}'
        result = requests.get(url).json()
        data['chart'] = draw_pie_chart(result)
        data['analyse_by'] = analyse_by
        data['analyse_options'] = analyse_options
        return render_template('tag_analysis.html', data=data)
    return render_template('tag_analysis.html', data=data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
