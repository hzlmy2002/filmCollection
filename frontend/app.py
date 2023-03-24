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

    # search based on title, director and actor
    search_column = request.args.get('search-choice', None, type=str)
    search_value = request.args.get('search-value', None, type=str)
    if (search_column and search_value):
        query_str = 'http://' + 'backend:5000' + \
            '/api/v1/search/' + search_column + '/' + search_value
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
    return render_template('movie_data_table.html', page=pagination, movies=movie_pl[pagination.start_index:pagination.end_index], genres=table_data.genres["all_genres"])


@app.route('/view-movie-data', methods=['GET'])
def movie_details():
    movie_title = request.args.get('title', 0, type=str)
    movie_details = requests.get(
        'http://' + 'backend:5000' + '/api/v1/searchv2/' + movie_title).json()
    print(movie_details)
    return render_template('movie_detail.html', movie_details=movie_details[0])


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


@app.route('/personality-analysis', methods=['GET', 'POST'])
def personality_analysis():
    data = {}
    data['traits'] = requests.get('http://backend:5000/api/v1/traits/get-all-traits').json()
    genres = requests.get('http://backend:5000/api/v1/view/all-genres').json()
    data['genres'] = genres['all_genres']

    # for a film, which personality trait liked it most?
    movieID = request.args.get('movieID', 0, type=str)
    title = request.args.get('title', 0, type=str)
    if movieID != 0 and title != 0:
        film_traits_ranking_url = f'http://backend:5000/api/v1/traits/film-traits-ranking/{movieID}'
        data['film_traits_ranking'] = requests.get(film_traits_ranking_url).json()
        data['film_traits_ranking_data'] = {"title": title}

    if request.method == 'POST':

        # for each personality trait, which films are given the highest/lowest ratings?
        trait_code = request.form.get('trait_film_ranking_trait')
        highest = request.form.get('trait_film_ranking_highest')
        if trait_code is not None and highest is not None:
            trait_film_ranking_url = f'http://backend:5000/api/v1/traits/trait-film-ranking/{trait_code}/{highest}'
            data['trait_film_ranking'] = requests.get(trait_film_ranking_url).json()
            data['trait_film_ranking_data'] = {"trait": data['traits'][int(trait_code)], "highest": ("Highest" if int(highest) == 1 else "Lowest")}

        # for each personality trait, what ratings do users usually give (across all films)?
        trait_code = request.form.get('trait_film_ratings_trait')
        if trait_code is not None:
            trait_film_ratings_url = f'http://backend:5000/api/v1/traits/trait-film-ratings/{trait_code}'
            ratings_percentages = requests.get(trait_film_ratings_url).json()
            data['trait_film_ratings'] = draw_ratings_pie_chart(ratings_percentages)
            data['trait_film_ratings_data'] = {"trait": data['traits'][int(trait_code)]}

        # for each personality trait, which genres are given the highest/lowest ratings?
        trait_code = request.form.get('trait_genre_ranking_trait')
        highest = request.form.get('trait_genre_ranking_highest')
        if trait_code is not None and highest is not None:
            trait_genre_ranking_url = f'http://backend:5000/api/v1/traits/trait-genre-ranking/{trait_code}/{highest}'
            data['trait_genre_ranking'] = requests.get(trait_genre_ranking_url).json()
            data['trait_genre_ranking_data'] = {"trait": data['traits'][int(trait_code)], "highest": ("Highest to lowest" if int(highest) == 1 else "Lowest to highest")}

        # for a genre, which personality trait liked/hated it most?
        genreID = request.form.get('genre_traits_ranking_genre')
        highest = request.form.get('genre_traits_ranking_highest')
        if genreID is not None and highest is not None:
            genre_traits_ranking_url = f'http://backend:5000/api/v1/traits/genre-traits-ranking/{genreID}/{highest}'
            data['genre_traits_ranking'] = requests.get(genre_traits_ranking_url).json()
            data['genre_traits_ranking_data'] = {"genre": data['genres'][int(genreID) - 1], "highest": ("Highest to lowest" if int(highest) == 1 else "Lowest to highest")}
        
        # for a genre, which degrees of a personality trait liked it most?
        genreID = request.form.get('genre_trait_range_genre')
        trait_code = request.form.get('genre_trait_range_trait')
        if genreID is not None and trait_code is not None:
            genre_trait_range_url = f'http://backend:5000/api/v1/traits/genre-trait-range/{trait_code}/{genreID}'
            data['genre_trait_range'] = requests.get(genre_trait_range_url).json()
            data['genre_trait_range_data'] = {"genre": data['genres'][int(genreID) - 1], "trait": data['traits'][int(trait_code)]}

    return render_template('personality_analysis.html', data=data)

def draw_ratings_pie_chart(results):
    labels = []
    values = []

    for range in results:
        labels.append(range[0] + ' ' + range[1] + ' ' + range[2])
        values.append(results[range])

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(values, labels=labels, autopct='%1.1f%%',
           pctdistance=0.9)
    legend_labels = [f'{l}, {s:1.1f}%' for l, s in zip(labels, values)]
    ax.legend(labels=legend_labels)

    chart = BytesIO()
    plt.savefig(chart, format='png')
    chart.seek(0)

    return base64.b64encode(chart.getvalue()).decode('utf-8')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
