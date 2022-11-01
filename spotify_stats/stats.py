import pandas as pd
import numpy as np
import spotipy

from spotify_stats.get_cover import get_cover_url


def check_whole_song_played(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check if the whole song was played.
    If 'reason_end' == 'trackdone' the whole song was played.
    """

    df["whole_played"] = np.where(
        df.reason_end == "trackdone", 1, 0)

    return df


def test_func(df: pd.DataFrame) -> None:
    """

    :param df:
    :return:
    """


def get_top_albums(
        df: pd.DataFrame,
        exclude_skipped: bool = True,
        top: int | None = 20,
        spotify_credentials: spotipy.client.Spotify | None = None,
        cover: bool = False,
        to_html: bool = True

) -> pd.DataFrame | str:
    """
    Returns the top albums determined by the count of number of songs
    that are played of a certain album.
    By default, top 20 albums are returned. Set cover to True to
    retrieve the URL of the album covers (Spotify credentials must
    be given). Returns the pandas data frame as html table.

    Arguments:
    ---------

    df: a pandas data frame with a spotify streaming history

    exclude_skipped: if true -> only consider songs which were
        not skipped

    top: int specifying the number of top albums

    spotify_credentials: provide spotify client id and secret
        to get album covers using the track uri

    cover: if true -> append the track uri

    to_html: render the resulting data frame as html for flask

    Example:
    -------

    >>> from spotipy.oauth2 import SpotifyClientCredentials
    >>> from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
    >>> spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET))
    >>> get_top_albums(df, top=3, cover=True, spotify_credentials=spotify, to_html=False)
          master_metadata_album_album_name  ...                                          cover_url
    0                       Flower Boy  ...  <img src='https://i.scdn.co/image/ab67616d0000...
    1                              TIM  ...  <img src='https://i.scdn.co/image/ab67616d0000...
    2                          Caracal  ...  <img src='https://i.scdn.co/image/ab67616d0000...
    [3 rows x 5 columns]

    """
    if exclude_skipped:
        # only consider songs which have been listened to entirely
        df = check_whole_song_played(df)

        df = df[df["whole_played"] == 1]

    # count how often is a song played of a certain album
    top_albums = df.value_counts(
        subset=["master_metadata_album_album_name", "master_metadata_album_artist_name"]
    ).reset_index(name="n_songs_album")

    # subset df
    df = df[["master_metadata_album_album_name",
             "master_metadata_album_artist_name",
             "spotify_track_uri"]]

    # only keep one instance of album name and artist name as only one track URI
    # is required to get a corresponding album cover
    df = df.drop_duplicates(
        subset=["master_metadata_album_album_name", "master_metadata_album_artist_name"])

    # merge df onto top albums
    top_albums = pd.merge(top_albums, df,
                          on=["master_metadata_album_album_name", "master_metadata_album_artist_name"],
                          how="inner")

    if top_albums is not None:
        top_albums = top_albums.nlargest(n=top, columns=["n_songs_album"])

    if cover and spotify_credentials is not None:
        # spotify client credentials must be given
        top_albums["cover_url"] = [get_cover_url(track_uri, spotify_credentials)
                                   for track_uri in top_albums["spotify_track_uri"]]

    if to_html:
        # return pandas data frame as html table
        # escape = False -> to 'render' links properly
        top_albums = top_albums.to_html(escape=False)

    return top_albums


def get_songs_played_by_artist(
        df: pd.DataFrame, exclude_skipped: bool = True,
        frequency: bool = False) -> pd.DataFrame:
    if exclude_skipped:
        # only consider songs which have been listened to entirely
        df = check_whole_song_played(df)

        df = df[df["whole_played"] == 1]

    if frequency:
        # count number of songs played by artist
        top_artists = pd.DataFrame(df["master_metadata_album_artist_name"].value_counts())

    else:
        # calculate sum of hours listened to artists
        top_artists = df.groupby(["master_metadata_album_artist_name"])["minutes_played"].sum().reset_index()

        # sort descending
        top_artists = top_artists.sort_values(by="minutes_played", ascending=False)

    return top_artists


def hours_listened(df: pd.DataFrame) -> tuple[int, int]:
    """
    Calculate hours and days listened to Spotify.
    """

    hours = (sum(df.minutes_played)) / 60

    days = hours / 24

    return hours, days


def get_most_played_songs(
        df: pd.DataFrame, exclude_skipped: bool = True,
        frequency: bool = False) -> pd.DataFrame:
    """
    Get most played songs of all time.
    """

    if exclude_skipped:
        # only consider songs which have been listened to entirely
        df = check_whole_song_played(df)

        df = df[df["whole_played"] == 1]

    if frequency:
        # count number of songs played by artist
        top_songs = pd.DataFrame(df["master_metadata_track_name"].value_counts())

    else:
        # calculate sum of hours listened to artists
        top_songs = df.groupby(["master_metadata_track_name"])["minutes_played"].sum().reset_index()

        # sort descending
        top_songs = top_songs.sort_values(by="minutes_played", ascending=False)

    return top_songs

# def most_skipped_artist
