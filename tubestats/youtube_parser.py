#!usr/bin/env python3
# tubestats/youtube_parser.py - returns channel ID from youtube video link, username
# 
# by Shivan Sivakumaran

import re

import googleapiclient

def channel_parser(youtube: googleapiclient.discovery.Resource, for_parse: str) -> str:
    """
    Parses user input from link to produce a channel ID

    params:
        youtube (googleapiclient.discovery)
        for_parse (str)
    :returns: channel_ID
    :rtype: str
    """
    if len(for_parse) == 11:         
        # video ID is 11 char long
        request = youtube.videos().list(
                part='snippet',
                id=for_parse,
                )
        response = request.execute()
        channel_ID = response['items'][0]['snippet']['channelId']
        return channel_ID
    elif len(for_parse) == 24:
        # channel ID is 24 char long
        return for_parse
    else:
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

def main():
    return

if __name__ == '__main__':
    main()
