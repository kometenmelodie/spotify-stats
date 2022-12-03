import os
import spotipy
import json
import plotly
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template
from spotify_stats.stats import (
    get_top_songs, get_top_artists, get_top_albums, get_top_skipped_songs,
    get_chart_hours_listened
)
from spotify_stats.style_tables import style_pandas_html_table

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
        top=20, spotify_credentials=spotify,
        cover=True)

    # pandas to html
    top_songs = style_pandas_html_table(
        data_frame=top_songs,
        table_heading="&#127911; Your top songs &#127911;")

    return top_songs


@app.route("/top-albums")
def display_top_albums():
    top_albums = get_top_albums(
        df, exclude_skipped=True, top=20,
        cover=True, spotify_credentials=spotify)

    # pandas to html
    top_albums = style_pandas_html_table(
        data_frame=top_albums,
        table_heading="&#127911; Your top albums &#127911;")

    return top_albums


@app.route("/top-artists")
def display_top_artists():
    top_artists = get_top_artists(
        df, exclude_skipped=True, top=20,
        artist_image=True, spotify_credentials=spotify)

    # pandas to html
    top_artists = style_pandas_html_table(
        data_frame=top_artists,
        table_heading="&#127911; Your top artists &#127911;")

    return top_artists


@app.route("/top-skipped-songs")
def display_top_skipped_tracks():
    top_skipped_tracks = get_top_skipped_songs(
        df, top=20,
        spotify_credentials=spotify,
        cover=True)

    # pandas to html
    top_skipped_tracks = style_pandas_html_table(
        data_frame=top_skipped_tracks,
        table_heading="&#127911; Your top skipped songs &#127911;")

    return top_skipped_tracks


@app.route("/hours-listened")
def display_bar_chart():
    bar_chart = get_chart_hours_listened(df)

    # Create graphJSON
    bar_chart_json = json.dumps(bar_chart, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("bar_chart.html", graphJSON=bar_chart_json)


if __name__ == "__main__":
    # to run in container
    app.run(host="0.0.0.0", port=80)

    # use app.run() if you are not containerizing the application
    # app.run()
