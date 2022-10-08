import pandas as pd
import numpy as np


def check_whole_song_played(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check if the whole song was played.
    If 'reason_end' == 'trackdone' the whole song was played.
    """

    df["whole_played"] = np.where(
        df.reason_end == "trackdone", 1, 0)

    return df


def get_songs_played_by_album(df: pd.DataFrame) -> pd.DataFrame:
    # only consider songs which have been listened to entirely
    df = check_whole_song_played(df)

    df = df[df["whole_played"] == 1]

    top_albums = pd.DataFrame(df["master_metadata_album_album_name"].value_counts())

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

# def most_skipped_artist