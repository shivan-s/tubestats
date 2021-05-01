#!usr/bin/env python3
# tests/test_youtube_parser.py - test for tubestates/youtube_parser.py 
# 
# by Shivan Sivakumaran

from tubestats.youtube_parser import channel_parser
from tubestats.youtube_api import create_api

import pytest

@pytest.fixture()
def youtubeapi():
    yt = create_api()
    return yt

def test_parser(youtubeapi):
    youtube = youtubeapi
    ALI_CHAN_ID = 'UCoOae5nYA7VqaXzerajD0lg'
    ALI_CHAN_LINK = 'https://www.youtube.com/channel/UCoOae5nYA7VqaXzerajD0lg'
    ALI_CHAN_LEGACY_NAME = 'Sepharoth64'
    ALI_CHAN_LEGACY_LINK = 'https://www.youtube.com/user/Sepharoth64'
    ALI_YT_LINK_long = 'https://www.youtube.com/watch?v=khQomXNzhkE'
    ALI_YT_LINK_partial = 'youtube.com/watch?v=khQomXNzhkE'
    ALI_YT_LINK_short = 'https://youtu.be/khQomXNzhkE'
    
    assert channel_parser(youtube, ALI_YT_LINK_long) == ALI_CHAN_ID
    assert channel_parser(youtube, ALI_YT_LINK_partial) == ALI_CHAN_ID
    assert channel_parser(youtube, ALI_YT_LINK_short) == ALI_CHAN_ID
    assert channel_parser(youtube, ALI_CHAN_LEGACY_LINK) == ALI_CHAN_ID
    assert channel_parser(youtube, ALI_CHAN_LINK) == ALI_CHAN_ID

  



