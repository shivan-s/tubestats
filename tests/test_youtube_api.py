#!usr/bin/env python3
# tests/test_youtube_api.py - testing YouTube API connection
#                           - testing if YouTube data is downloaded
#
# by Shivan Sivakumaran

from tubestats.youtube_api import create_api, YouTubeAPI
from tests.test_settings import set_channel_ID_test_case

from pathlib import Path
import pickle

import pytest

import googleapiclient
import pandas

def test_create_api():
    youtube = create_api()
    assert isinstance(youtube, googleapiclient.discovery.Resource)

@pytest.fixture()
def youtubeapi():
    channel_ID = set_channel_ID_test_case()
    yt = YouTubeAPI(channel_ID)
    return yt

def test_get_channel_data(youtubeapi):
    channel_data = youtubeapi.get_channel_data()
    assert isinstance(channel_data, dict)
    # assert channel_data['channel_name'] == 'Ali Abdaal'
     
    # saving channel data for API calls later on
    BASE_DIR = Path(__file__).parent.parent
    with open(BASE_DIR / 'tests' / 'data' / 'channel_data.pkl', 'wb') as p:
        pickle.dump(channel_data, p)

def test_get_video_data(youtubeapi):
    df = youtubeapi.get_video_data()
    assert isinstance(df, pandas.core.frame.DataFrame)

    # saving video data to save API calls for later testing
    BASE_DIR = Path(__file__).parent.parent
    df.to_pickle(BASE_DIR / 'tests' / 'data' / 'video_data.pkl')
