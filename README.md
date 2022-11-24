# Spotify-stats

`Spotify-stats` is a `Python` package to get enhanced statistics about your listening habits.
Spotify Rewind (Spotify's own statistics) always focuses on a single year. On the other hand,
`Spotify-stats` uses your entire streaming history and lets you visualize your top artists,
top albums, top songs and most skipped songs.

A flask app is included and provides a basic interface to browse your stats. The app can be run using a
`docker` container. Unlike other spotify statistics websites, `Spotify-stats` does not track any information
and runs locally. Under the hood `Spotify-stats` uses
your streaming history and [`spotipy`](https://spotipy.readthedocs.io/en/2.21.0/) (a `Python` package
for the `Spotify Web API`) to retrieve album covers. Hence, some prerequisites are needed.

# Prerequisites

As mentioned a streaming history and developer access to the `Spotify Web API` are needed.
First retrieve your streaming history. Simply write an e-mail to `privacy@spotify.com` and request your
listening history. After two days I got a confirmation mail stating that my data is being collected. After
another 12 days Spotify provided me a download link for my data (a bunch of json files).

Next, visit the [Spotify developer site](https://developer.spotify.com/) as you will need access to the `Spotify Web API`.
Log in with your Spotify account and click on Dashboard. Here we have to create an app. Provide an app name and description.
After creation, you will get a client ID and client secret. `spotipy` requires these credentials.

Now after a quick set-up you can start to use the package.

# Set-up

## Create streaming history file

First, create a csv from your streaming history. Create a `Python` file with following content:

```python
from spotify_stats.get_streams import get_streams

# streaming history to csv from json files
df = get_streams("path-to-your-json-files")

df.to_csv("streaming_history.csv", index=False)
```

## Use Spotify developer credentials

Simply place your Spotify developer credentials to the `.env` file and make sure to never expose your credentials.

# Usage

## With docker

You can build or own docker container with the `Dockerfile` provided which will run the flask app locally.

Build the image:
```commandline
sudo docker build -t <image_name> .
```

And run the image:
```commandline
sudo docker run -d -p 80:80 <image_name>
```

Now visit `localhost:80` in your browser.

## Without docker

If you wish to run the flask app `app.py` without docker. Uncomment the last line in the file:
```python
if __name__ == "__main__":
    # to run in container
    #app.run(host="0.0.0.0", port=80)

    # use app.run() if you are not containerizing the application
    app.run()
```

Next, automatically install the dependencies in a new virtual environment using the commands:
```commandline
python -m pip install poetry
python -m poetry install
```

Now you can just run `app.py`.

## I just want to use the package

Run
```commandline
python -m pip install poetry
python -m poetry install
```
to install dependencies.

A quick example on how to use the `Python` package on its own:

```python
import os
from spotify_stats.stats import get_top_albums
from dotenv import load_dotenv
import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials

# get Spotify developer credentials
load_dotenv()

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        os.getenv("SPOTIFY_CLIENT_ID"),
        os.getenv("SPOTIFY_CLIENT_SECRET")
    ))

df = pd.read_csv("streaming_history.csv")

top_albums = get_top_albums(
    df, exclude_skipped=True, top=50,
    cover=True, spotify_credentials=spotify)
```
