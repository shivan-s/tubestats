"""Fixture for testing."""

import pickle
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from tubestats.data import YouTubeData


@pytest.fixture
def set_channel_ID_test_case() -> str:
    """Set channel ID for test.

    Sets channel test ID

    Returns:
        (str): channel id
    """
    # set this to desired channel
    CHANNEL = "shiv"

    test_channels = {
        "ali": "UCoOae5nYA7VqaXzerajD0lg",  # Ali Abdaal
        "shiv": "UCrbYXWUmeCy4GqArthu4hCw",  # Shivan Sivakumaran (me)
        "dbourke": "UCr8O8l5cCX85Oem1d18EezQ",  # Daniel Bourke
    }
    channel_ID = test_channels[CHANNEL]
    return channel_ID


@pytest.fixture()
def youtubedata():
    """Give YouTube data."""
    BASE_DIR = Path(__file__).parent.parent
    channel_ID = set_channel_ID_test_case()

    # uses saved data instead of calling the API
    with open(BASE_DIR / "tests" / "data" / "channel_data.pkl", "rb") as p:
        channel_data = pickle.load(p)

    df = pd.read_pickle(BASE_DIR / "tests" / "data" / "video_data.pkl")

    yd = YouTubeData(channel_ID=channel_ID, channel_data=channel_data, df=df)
    return yd


@pytest.fixture()
def with_dates(youtubedata):
    """Provide dates."""
    date_start = datetime(2017, 6, 30)
    date_end = datetime(2017, 12, 30)
    df = youtubedata.transform_dataframe(date_start, date_end)
    return df
