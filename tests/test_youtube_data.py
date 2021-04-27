#!usr/bin/env python3
# test/test_youtube_data.py - testing data wrangling
#                           - testing graph output
# by Shivan Sivakumaran

from tubestats.youtube_data import YouTubeData

import pickle
from pathlib import Path
from datetime import datetime, timedelta

import pytest
import pandas
import numpy
import altair

# TODO: write tests

@pytest.fixture()
def youtubedata():
    ALI_ABDAAL_CHANNEL_ID = 'UCoOae5nYA7VqaXzerajD0lg'
    BASE_DIR = Path(__file__).parent.parent
    
    # uses saved data instead of calling the API
    with open(BASE_DIR / 'data' / 'channel_data.pkl', 'rb') as p:
        channel_data = pickle.load(p)
    
    df = pandas.read_pickle(BASE_DIR / 'data' / 'video_data.pkl')
    
    yd = YouTubeData(ALI_ABDAAL_CHANNEL_ID, channel_data=channel_data, df=df)
    return yd

def test_channel_name(youtubedata):
    name = youtubedata.channel_name()
    assert name == 'Ali Abdaal'

def test_video_count(youtubedata):
    count = youtubedata.video_count()
    assert isinstance(count, int)
    
def test_start_date(youtubedata):
    date = youtubedata.start_date()
    assert isinstance(date, str)

def test_thumbnail_url(youtubedata):
    thumb = youtubedata.thumbnail_url()
    assert isinstance(thumb, str)
    assert thumb == 'https://yt3.ggpht.com/ytc/AAUvwnjTeFYoj5eDtxHLIiF36qp7yCZTp4q8mxIKLjWx=s800-c-k-c0x00ffffff-no-rj'

def test_channel_description(youtubedata):
    desc = youtubedata.channel_description()
    assert isinstance(desc, str)
    # TODO: better test case

def test_raw_dataframe(youtubedata):
    raw_df = youtubedata.raw_dataframe()
    assert isinstance(raw_df, pandas.core.frame.DataFrame)

def test_dataframe(youtubedata):
    df = youtubedata.dataframe()
    assert isinstance(df, pandas.core.frame.DataFrame)

def test_total_channel_views(youtubedata):
    views = youtubedata.total_channel_views()
    assert isinstance(views, numpy.int64)

def test_total_watchtime(youtubedata):
    wt = youtubedata.total_watchtime()
    assert isinstance(wt, timedelta)

def test_total_comments(youtubedata):
    comments = youtubedata.total_comments()
    assert isinstance(comments, numpy.int64)

def test_tranform_dataframe(youtubedata):
    date_start = datetime(2017, 6, 30) 
    date_end = datetime(2017, 12, 30)
    df = youtubedata.transform_dataframe(date_start, date_end)
    assert isinstance(df, pandas.core.frame.DataFrame)
    assert len(df) == 56

def test_scatter_all_videos(youtubedata):
    date_start = datetime(2017, 6, 30) 
    date_end = datetime(2017, 12, 30)
    df = youtubedata.transform_dataframe(date_start, date_end)
    c = youtubedata.most_viewed_videos(df)
    assert isinstance(c, altair.vegalite.v4.api.Chart)

