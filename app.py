import streamlit as st
import pickle
import pandas as pd
import requests
import os


# Function to fetch movie poster from OMDb API
def fetch_poster(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey=d25c9184"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        data = response.json()

        # Check if 'Poster' exists in response data
        if "Poster" in data and data["Poster"] and data["Poster"] != "N/A":
            return data["Poster"]
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"  # Fallback image

    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=No+Image"  # Fallback image


# Function to recommend movies
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in database.")
        return [], []

    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movie_posters = []

    for i in movies_list:
        movie_data = movies.iloc[i[0]]
        recommended_movies.append(movie_data.title)
        recommended_movie_posters.append(fetch_poster(movie_data.title))  # Fetch poster using title

    return recommended_movies, recommended_movie_posters


# Load movie data
try:
    if os.path.exists('movie_dict.pkl') and os.path.exists('similarity.pkl'):
        with open('movie_dict.pkl', 'rb') as f:
            movies_dict = pickle.load(f)
        with open('similarity.pkl', 'rb') as f:
            similarity = pickle.load(f)

        movies = pd.DataFrame(movies_dict)
    else:
        raise FileNotFoundError("Missing data files: Ensure 'movie_dict.pkl' and 'similarity.pkl' exist.")

except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
    st.error(f"Error loading data: {e}")
    movies = pd.DataFrame({"title": []})  # Empty DataFrame fallback
    similarity = []

# Streamlit UI
st.title('Movie Recommender System')

if not movies.empty:
    selected_movie_name = st.selectbox(
        'Type or select a movie from the dropdown',
        movies['title'].values
    )

    if st.button('Recommend'):
        if not selected_movie_name:
            st.error("Please select a movie.")
        else:
            recommendations, posters = recommend(selected_movie_name)

            if not recommendations:
                st.warning("No recommendations found.")
            else:
                cols = st.columns(len(recommendations))
                for col, name, poster in zip(cols, recommendations, posters):
                    with col:
                        st.text(name)
                        st.image(poster)
else:
    st.error("Movie data is not available.")
