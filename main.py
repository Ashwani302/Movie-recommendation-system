import pandas as pd
import pickle
import numpy as np
from flask import Flask, render_template, request

# Load files
movie_dict = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))
reviews = pd.read_csv("updated_csv_file_with_imdb.csv")


# Recommend movies based on similarity index
def rec(movie_title):
    movie_title = movie_title.lower()
    if movie_title not in movies['title'].str.lower().unique():
        return 'Sorry! The movie is not in our database.'
    else:
        movie_ind = movies[movies['title'].str.lower() == movie_title].index[0]
        distance = similarity[movie_ind]
        movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:11]

        recommend_movies = []
        for i in movie_list:
            recommend_movies.append(movies.iloc[i[0]].title)

        return recommend_movies


def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["', '')
    my_list[-1] = my_list[-1].replace('"]', '')
    return my_list


def get_suggestions():
    return list(movies['title'].str.capitalize())


# Flask API
app = Flask(__name__)

@app.route("/") 
@app.route("/index")
def home():
    suggestions = get_suggestions()  # returning suggestions in search box
    return render_template('index.html', suggestions=suggestions)

@app.route("/similarity", methods=["POST"])
def similarity_route():
    movie = request.form['name']
    rc = rec(movie)
    if isinstance(rc, str):  # Check if rc is a string (error message)
        return rc
    else:
        m_str = "---".join(rc)
        return m_str

@app.route("/recommend", methods=["POST"])
def recommend():
    # Getting data from AJAX request
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']
    
    # Get movie suggestions for auto-complete
    suggestions = get_suggestions()

    # Convert strings to lists
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)
    
    # Convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = cast_ids.strip("[]").split(',')

    # Rendering the string to Python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '\"')
    
    # Combining multiple lists as a dictionary for the HTML file
    movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}

    casts = {cast_names[i]: [cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}
    
    cast_details = {cast_names[i]: [cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}

    # Filter reviews based on the current movie's IMDb ID
    movie_reviews = reviews[reviews['IMDb ID'] == imdb_id][['Author', 'Review', 'Sentiment Emoji']].to_dict(orient='records')

    # Passing all the data to the HTML file
    return render_template('recommend.html', title=title, poster=poster, overview=overview,
                           vote_average=vote_average, vote_count=vote_count, release_date=release_date,
                           runtime=runtime, status=status, genres=genres, movie_cards=movie_cards,
                           reviews=movie_reviews, casts=casts, cast_details=cast_details)

if __name__ == '__main__':
    app.run(debug=True)
