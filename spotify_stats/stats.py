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
       Place  ... Number of songs played
    0      1  ...                   1228
    1      2  ...                   1005
    2      3  ...                    861
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

    if top is not None:
        top_albums = top_albums.nlargest(n=top, columns=["n_songs_album"])

    if cover and spotify_credentials is not None:
        # spotify client credentials must be given
        top_albums["Cover"] = [get_cover_url(track_uri, spotify_credentials)
                               for track_uri in top_albums["spotify_track_uri"]]

    # drop spotify track URI
    top_albums = top_albums.drop(columns=["spotify_track_uri"])

    # rename columns
    top_albums.columns = ["Album", "Artist", "Number of songs played", "Cover"]

    # new column "Place"
    top_albums["Place"] = [i for i in range(1, len(top_albums) + 1)]

    # reorder columns
    top_albums = top_albums.reindex(
        columns=["Place", "Cover", "Album", "Artist", "Number of songs played"])

    if to_html:
        # return pandas data frame as html table
        # escape = False -> to 'render' links properly
        top_albums = top_albums.to_html(escape=False, index=False)

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


def get_top_songs(
        df: pd.DataFrame, exclude_skipped: bool = True,
        frequency: bool = False, top: int | None = 20,
        spotify_credentials: spotipy.client.Spotify | None = None,
        cover: bool = False,
        to_html: bool = True
) -> pd.DataFrame:
    """
    Get most played songs.

    Arguments:
    ---------

    df: a pandas data frame with a spotify streaming history

    exclude_skipped: if true -> only consider streams which were
        not skipped

    frequency: if False -> return the times a song was streamed.
        if True -> returns hours a specific song was streamed.

    top: int specifying the number of top songs

    spotify_credentials: provide spotify client id and secret
        to get album covers using the track uri

    cover: if true -> append the track uri

    to_html: render the resulting data frame as html for flask

    Example:
    -------

    >>> from spotipy.oauth2 import SpotifyClientCredentials
    >>> from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

    >>> top_songs = get_top_songs(
            df, exclude_skipped=True, frequency=True,
            top=3, spotify_credentials=spotify,
            cover=True, to_html=False
        )
    Place  ... Times played
    0      1  ...          216
    1      2  ...          191
    2      3  ...          177
    [3 rows x 6 columns]

    """

    if exclude_skipped:
        # only consider songs which have been listened to entirely
        df = check_whole_song_played(df)

        df = df[df["whole_played"] == 1]

    if frequency:
        # count the number a song was played by specific track, album and artist name
        top_songs = df.value_counts(
            subset=["master_metadata_track_name",
                    "master_metadata_album_album_name",
                    "master_metadata_album_artist_name"]
        ).reset_index(name="n_played")

    if frequency is False:
        # calculate sum of hours listened to song
        top_songs = df.groupby([
            "master_metadata_track_name",
            "master_metadata_album_album_name",
            "master_metadata_album_artist_name"
        ])[
            "minutes_played"].sum().reset_index()

        top_songs["Hours played"] = [round(track / 60, 2) for track in top_songs["minutes_played"]]

        # sort descending
        top_songs = top_songs.sort_values(by="Hours played", ascending=False)

        # drop minutes_played
        top_songs = top_songs.drop(columns=["minutes_played"])

    # subset df
    df = df[["master_metadata_track_name",
             "master_metadata_album_album_name",
             "master_metadata_album_artist_name",
             "spotify_track_uri"]]

    # only keep one instance of track, album and artist name as only one track URI
    # is required to get a corresponding album cover
    # track URI can change over time
    df = df.drop_duplicates(
        subset=["master_metadata_track_name", "master_metadata_album_album_name",
                "master_metadata_album_artist_name"])

    # merge df onto top songs
    top_songs = pd.merge(top_songs, df,
                         on=["master_metadata_track_name", "master_metadata_album_album_name",
                             "master_metadata_album_artist_name"],
                         how="inner")

    if top is not None:
        if frequency:
            top_songs = top_songs.nlargest(n=top, columns=["n_played"])
        if frequency is False:
            top_songs = top_songs.nlargest(n=top, columns=["Hours played"])

    if cover and spotify_credentials is not None:
        # spotify client credentials must be given
        top_songs["Cover"] = [get_cover_url(track_uri, spotify_credentials)
                              for track_uri in top_songs["spotify_track_uri"]]

    # drop spotify track URI
    top_songs = top_songs.drop(columns=["spotify_track_uri"])

    # rename columns
    top_songs.columns = ["Track", "Album", "Artist", "Times played", "Cover"]

    # new column "Place"
    top_songs["Place"] = [i for i in range(1, len(top_songs) + 1)]

    # reorder columns
    top_songs = top_songs.reindex(
        columns=["Place", "Cover", "Track", "Album", "Artist", "Times played"])

    if frequency is False:
        # rename column
        top_songs = top_songs.rename(columns={"Times played": "Hours listened"})

    if to_html:
        # return pandas data frame as html table
        # escape = False -> to 'render' links properly
        top_songs = top_songs.to_html(escape=False, index=False)

    return top_songs


def get_top_skipped_songs(
        df: pd.DataFrame, top: int | None = 20,
        spotify_credentials: spotipy.client.Spotify | None = None,
        cover: bool = False,
        to_html: bool = True
) -> pd.DataFrame:
    """
    Get most skipped songs.

    Arguments:
    ---------

    df: a pandas data frame with a spotify streaming history

    top: int specifying the number of top skipped songs

    spotify_credentials: provide spotify client id and secret
        to get album covers using the track uri

    cover: if true -> append the track uri

    to_html: render the resulting data frame as html for flask

    Example:
    -------

    >>> from spotipy.oauth2 import SpotifyClientCredentials
    >>> from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

    >>> top_songs = get_top_skipped_songs(
            df, top=3, spotify_credentials=spotify,
            cover=True, to_html=False)
       Place  ... Times skipped
    0      1  ...           122
    1      2  ...           103
    2      3  ...            97
    [3 rows x 6 columns]
    """

    # only consider skipped record entries
    df = check_whole_song_played(df)

    df = df[df["whole_played"] == 0]

    # count the number a song was skipped by specific track, album and artist name
    top_skipped_songs = df.value_counts(
        subset=["master_metadata_track_name",
                "master_metadata_album_album_name",
                "master_metadata_album_artist_name"]
    ).reset_index(name="n_skipped")

    # subset df
    df = df[["master_metadata_track_name",
             "master_metadata_album_album_name",
             "master_metadata_album_artist_name",
             "spotify_track_uri"]]

    # only keep one instance of track, album and artist name as only one track URI
    # is required to get a corresponding album cover
    # track URI can change over time
    df = df.drop_duplicates(
        subset=["master_metadata_track_name", "master_metadata_album_album_name",
                "master_metadata_album_artist_name"])

    # merge df onto top songs
    top_skipped_songs = pd.merge(top_skipped_songs, df,
                                 on=["master_metadata_track_name", "master_metadata_album_album_name",
                                     "master_metadata_album_artist_name"],
                                 how="inner")

    if top is not None:
        top_skipped_songs = top_skipped_songs.nlargest(n=top, columns=["n_skipped"])

    if cover and spotify_credentials is not None:
        # spotify client credentials must be given
        top_skipped_songs["Cover"] = [get_cover_url(track_uri, spotify_credentials)
                                      for track_uri in top_skipped_songs["spotify_track_uri"]]

    # drop spotify track URI
    top_skipped_songs = top_skipped_songs.drop(columns=["spotify_track_uri"])

    # new column "Place"
    top_skipped_songs["Place"] = [i for i in range(1, len(top_skipped_songs) + 1)]

    # rename columns
    new_names = ["Track", "Album", "Artist", "Times skipped", "Place"]

    if "Cover" not in top_skipped_songs.columns:
        top_skipped_songs.columns = new_names
        # reorder columns
        top_skipped_songs = top_skipped_songs.reindex(
            columns=["Place", "Track", "Album", "Artist", "Times skipped"]
        )

    if "Cover" in top_skipped_songs.columns:
        new_names.insert(-1, "Cover")
        top_skipped_songs.columns = new_names
        # reorder columns
        top_skipped_songs = top_skipped_songs.reindex(
            columns=["Place", "Cover", "Track", "Album", "Artist", "Times skipped"])

    if to_html:
        # return pandas data frame as html table
        # escape = False -> to 'render' links properly
        top_skipped_songs = top_skipped_songs.to_html(escape=False, index=False)

    return top_skipped_songs
