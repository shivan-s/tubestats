#!/env/bin/python3
# tests/test_helper.py - testing for tubestates/helper.py


from datetime import datetime

import pytest

from tubestats.helpers import create_api, VideoData, DataFunctions

def test_create_api():
    youtube = create_api()

@pytest.fixture() 
def videodata():
    ALI_ABDAAL_CHANNEL_ID = 'UCoOae5nYA7VqaXzerajD0lg'
    yt = VideoData(ALI_ABDAAL_CHANNEL_ID)
    return yt

def test_constructor(videodata):
    assert isinstance(videodata, VideoData)

def test_get_channel_data(videodata):
    channel_data = videodata.get_channel_data()
    assert type(channel_data) == dict
    assert channel_data['channel_name'] == 'Ali Abdaal'

def test_get_video_data(videodata):
    df = videodata.get_video_data()
    assert len(df) > 363

def test_load_video_data(videodata):
    df = videodata.load_video_data()
    assert len(df) > 363

@pytest.fixture()
def datafunctions():
    ALI_ABDAAL_CHANNEL_ID = 'UCoOae5nYA7VqaXzerajD0lg'
    dataf = DataFunctions(ALI_ABDAAL_CHANNEL_ID)
    return dataf

def test_constructor(datafunctions):
    assert isinstance(datafunctions, DataFunctions)

def test_channel_name(datafunctions):
    channel_name = datafunctions.channel_name()
    assert channel_name == 'Ali Abdaal'

def test_video_count(datafunctions):
    channel_video_count = datafunctions.video_count()
    assert channel_video_count > 363

def test_start_date(datafunctions):
    channel_start_date = datafunctions.start_date()
    assert channel_start_date == '20 November 2007'
   

def test_thumbnail_url(datafunctions):
    channel_thumbnail_url = datafunctions.thumbnail_url()
    assert channel_thumbnail_url is not None

def test_channel_description(datafunctions):
    channel_description = datafunctions.channel_description()
    assert channel_description is not None

def test_dataframe(datafunctions):
    df = datafunctions.dataframe()
    assert df is not None

def test_total_stat(datafunctions):
    total = total_stat(stat_type='view')
    assert int(total) > 1

def test_tranform_dataframe(datafunctions):
    date_start = datetime(2017, 1, 1) 
    date_end = datetime(2018, 1, 1)
    df = datafunctions.dataframe(date_start=date_start, date_end=date_end)
    assert df is not None

def test_scatter_all_videos(datafunctions):
    pass

def test_(datafunctions):
    pass

def test_most_viewed_videos(datafunctions):
    preserved_df, title, link = datafunctions.most_viewed_videos()

