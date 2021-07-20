#!usr/bin/env python3
# test/test_youtube_data.py - testing data wrangling
#                           - testing graph output
# by Shivan Sivakumaran

from tubestats.youtube_data import YouTubeData
from tests.test_settings import set_channel_ID_test_case

import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

import pytest
import pandas
import numpy
import altair


@pytest.fixture()
def youtubedata():
    BASE_DIR = Path(__file__).parent.parent
    channel_ID = set_channel_ID_test_case() 

    # uses saved data instead of calling the API
    with open(BASE_DIR / 'tests' / 'data' / 'channel_data.pkl', 'rb') as p:
        channel_data = pickle.load(p)
    
    df = pandas.read_pickle(BASE_DIR / 'tests' / 'data' / 'video_data.pkl')
    
    yd = YouTubeData(channel_ID=channel_ID, channel_data=channel_data, df=df)
    return yd

def test_channel_name(youtubedata):
    name = youtubedata.channel_name()
    assert isinstance(name, str)
    # assert name == 'Ali Abdaal'

def test_video_count(youtubedata):
    count = youtubedata.video_count()
    assert isinstance(count, int)
    
def test_start_date(youtubedata):
    date = youtubedata.start_date()
    assert isinstance(date, str)

def test_thumbnail_url(youtubedata):
    thumb = youtubedata.thumbnail_url()
    assert isinstance(thumb, str)
    # assert thumb == 'https://yt3.ggpht.com/ytc/AAUvwnjTeFYoj5eDtxHLIiF36qp7yCZTp4q8mxIKLjWx=s800-c-k-c0x00ffffff-no-rj'

def test_channel_description(youtubedata):
    desc = youtubedata.channel_description()
    assert isinstance(desc, str)

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

@pytest.fixture()
def with_dates(youtubedata):
    date_start = datetime(2017, 6, 30) 
    date_end = datetime(2017, 12, 30)
    df = youtubedata.transform_dataframe(date_start, date_end)
    return df

def test_tranform_dataframe(with_dates):
    df = with_dates
    assert isinstance(df, pandas.core.frame.DataFrame)
    # assert len(df) == 56

def test_scatter_all_videos(with_dates, youtubedata):
    df = with_dates
    c = youtubedata.scatter_all_videos(df)
    assert isinstance(c, altair.vegalite.v4.api.Chart)

def test_most_viewed_videos(with_dates, youtubedata):
    df = with_dates
    most_viewed = youtubedata.most_viewed_videos(df)
    assert isinstance(most_viewed, dict)

def test_most_disliked_videos(with_dates, youtubedata):
    df = with_dates
    most_disliked = youtubedata.most_disliked_videos(df)
    assert isinstance(most_disliked, dict)

@pytest.fixture()
def time_difference(with_dates, youtubedata):
    df = with_dates
    df_with_td = youtubedata.time_difference_calculate(df)
    return df_with_td

def test_time_difference_calculate(time_difference):
    df_with_td = time_difference
    assert isinstance(df_with_td, pandas.core.frame.DataFrame)

def test_list_time_difference_ranked(time_difference, youtubedata):
    df = time_difference
    time_diff = youtubedata.list_time_difference_ranked(df)
    assert isinstance(time_diff, pandas.core.frame.DataFrame)

def test_time_difference_plot(time_difference, youtubedata):
    df = time_difference 
    c = youtubedata.time_difference_plot(df)
    assert isinstance(c, altair.vegalite.v4.api.Chart)

def test_time_difference_statistics(time_difference, youtubedata):
    df = time_difference
    quan = youtubedata.time_difference_statistics(df)
    assert isinstance(quan, dict)

def test_greatest_time_difference_video(time_difference, youtubedata):
    df = time_difference
    vid_list = youtubedata.greatest_time_difference_video(df) 
    assert isinstance(vid_list, dict)
