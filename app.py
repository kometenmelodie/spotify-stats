import os
import spotipy
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template
from spotify_stats.stats import (
    get_top_songs, get_top_artists, get_top_albums, get_top_skipped_songs
)

from spotipy.oauth2 import SpotifyClientCredentials

# get Spotify developer credentials
load_dotenv()

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        os.getenv("SPOTIFY_CLIENT_ID"),
        os.getenv("SPOTIFY_CLIENT_SECRET")
    ))

df = pd.read_csv("streaming_history.csv")

app = Flask(__name__)


@app.route("/")
def welcome():
    return render_template("index.html")


@app.route("/top-songs")
def display_top_songs():
    top_songs = get_top_songs(
        df, exclude_skipped=True, frequency=True,
        top=50, spotify_credentials=spotify,
        cover=True, to_html=True)

    return top_songs


@app.route("/top-albums")
def display_top_albums():
    top_albums = get_top_albums(
        df, exclude_skipped=True, top=50,
        cover=True, spotify_credentials=spotify, to_html=True)

    return top_albums


@app.route("/top-artists")
def display_top_artists():
    top_artists = get_top_artists(
        df, exclude_skipped=True, top=50,
        artist_image=True, spotify_credentials=spotify, to_html=True)

    return top_artists


@app.route("/top-skipped-songs")
def display_top_skipped_tracks():
    top_skipped_tracks = get_top_skipped_songs(
        df, top=50,
        spotify_credentials=spotify,
        cover=True, to_html=True)

    return top_skipped_tracks


if __name__ == "__main__":
    # to run in container
    # app.run(host="0.0.0.0", port=80)

    # use app.run() if you are not containerizing the application
    app.run()
