import requests
import spotipy
from PIL import Image


def get_cover_image(
        track_uri: str, spotify_credentials: spotipy.client.Spotify,
        out_path: str = None
) -> Image:
    """
    Use spotipy to retrieve a cover as PNG of a Spotify track URI.
    Needs spotify developer credentials.
    """

    # get track info
    track = spotify_credentials.track(track_uri)

    # url to cover
    cover_url = track["album"]["images"][2]["url"]

    # retrieve cover
    response = requests.get(cover_url, stream=True)

    cover = Image.open(response.raw)

    if out_path is not None:
        cover.save(out_path, format="PNG")

    return cover


def get_cover_url(
        track_uri: str, spotify_credentials: spotipy.client.Spotify
) -> str:
    """
    Get link to the cover in order to display it in html.
    """

    # get track info
    track = spotify_credentials.track(track_uri)

    # url to smaller cover
    cover_url = track["album"]["images"][1]["url"]

    # return as html
    cover_html = "<img src='" + cover_url + "'>"

    return cover_html
