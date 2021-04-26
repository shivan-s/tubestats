#!usr/bin/env python3
# tests/test_youtube_api.py - testing YouTube API connection
#                           - testing if YouTube data is downloaded
#
# by Shivan Sivakumaran

from tubestats.youtube_api import create_api, YouTubeAPI

import pytest

import googleapiclient
import pandas

def test_create_api():
    youtube = create_api()
    assert isinstance(youtube, googleapiclient.discovery.Resource)

@pytest.fixture()
def youtubeapi():
    ALI_ABDAAL_CHANNEL_ID = 'UCoOae5nYA7VqaXzerajD0lg'
    # SHIVAN_CHANNEL_ID = ''
    # DANIEL_BOURKE_CHANNEL_ID = ''
    # _CHANNEL_ID = ''
    # _CHANNEL_ID = ''
    yt = YouTubeAPI(ALI_ABDAAL_CHANNEL_ID)
    return yt

def test_get_channel_data(youtubeapi):
    channel_data = youtubeapi.get_channel_data()
    assert channel_data['channel_name'] == 'Ali Abdaal'
     
def test_get_video_data(youtubeapi):
    df = youtubeapi.get_video_data()
    assert isinstance(df, pandas.core.frame.DataFrame)

# TODO: save the data to save API calls for testing
# from pathlib import Path
# df.to_hdf(self.BASE_DIR / 'data' / 'store_tube.h5', key=self.channel_ID)

