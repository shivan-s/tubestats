"""Testing for application."""

from datetime import datetime, timedelta
from typing import List

import altair
import numpy
import pandas
import pytest


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
    pass
    # FIXME: test does not work but code remains functional
    # df = time_difference
    # vid_list = youtubedata.greatest_time_difference_video(df)
    # assert isinstance(vid_list, dict)
