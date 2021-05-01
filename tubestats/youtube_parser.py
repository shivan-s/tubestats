#!usr/bin/env python3
# tubestats/youtube_parser.py - returns channel ID from youtube video link, username
# 
# by Shivan Sivakumaran

from tubestats.youtube_api import create_api

import googleapiclient

import re

def channel_parser(youtube: googleapiclient.discovery, for_parse: str) -> str:
   
    #TODO video Id is len() = 11
    # TODO chan ID length is 25?


    # TODO: Parses link to work about chan id. # test and works
    LINK_MATCH = r'(^.*youtu)(\.be|be\.com)(\/watch\?v\=|\/)([a-zA-Z0-9_-]+)(\/)?([a-zA-Z0-9_-]+)?'
    m = re.search(LINK_MATCH, for_parse)
    video_id = m.group(4)

    if video_id == 'channel':
        return m.group(6)

    elif video_id == 'user':
        channel_username = m.group(6)
        request = youtube.channels().list(
                part='snippet',
                forUsername=channel_username,
                )
        response = request.execute()
        channel_ID = response['items'][0]['id']
        return channel_ID
        
    else:
        request = youtube.videos().list(
                part='snippet',
                id=video_id,
                )
        response = request.execute()
        channel_ID = response['items'][0]['snippet']['channelId']
        return channel_ID




    # TODO: obtain the channel ID



    youtube = create_api()



def main():
    return

if __name__ == '__main__':
    main()
