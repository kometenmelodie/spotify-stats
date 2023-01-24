from os import listdir

import pandas as pd


def get_streams(path: str) -> pd.DataFrame:
    """
    Construct a data frame for all given json files.
    The data frame contains the streaming history sorted
    by the date a song was played.
    """
    files = [path + x for x in listdir(path) if x.startswith("endsong_")]

    files = sorted(files)

    # empty list to store data frames
    dfs = []
    for file in files:
        data = pd.read_json(file)
        dfs.append(data)

    df = pd.concat(dfs, ignore_index=True)

    # sort by timestamp
    df = df.sort_values(by=["ts"])

    # calculate seconds played
    df["seconds_played"] = df.ms_played / 1000

    # calculate minutes played
    df["minutes_played"] = df.seconds_played / 60

    return df
