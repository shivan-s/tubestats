#!usr/bin/env python3
# tubestats/youtube_api - connects to YouTube API
#                       - authenticates API_LIMIT
#                       - downloads data based on channel ID
#                       - returns pandas dataframe
#
# by Shivan Sivakumaran

import os
import math
import logging
import threading
from typing import Dict

from dotenv import load_dotenv
import pandas as pd
import googleapiclient.discovery
import googleapiclient.errors

from tubestats.youtube_parser import channel_parser

def create_api() -> googleapiclient.discovery.Resource:
        """
        Creates an authenticated api client
        
        :params: None
        :return: authenticated api client
        :rtype: googleapiclient.discovery.Resource
        """
        load_dotenv()
        api_service_name = 'youtube'
        api_version = 'v3'
        try:
            youtube = googleapiclient.discovery.build(api_service_name,
                    api_version,
                    developerKey=os.getenv('YT_API_KEY'))
        except Exception as e:
            logging.error('Error on creating API', exc_info=True)
        return youtube

class YouTubeAPI:
    """
    This connects to the YouTube API, also includes methods to download video data

    :params:
        user_input (str)
    :methods:
        get_channel_data(): returns channel data
        get_video_data(): gets videos data 
    """
    def __init__(self, user_input: str):
        self.youtube = create_api()
        self.user_input = user_input
        self.channel_ID = channel_parser(self.youtube, self.user_input)

    def get_channel_data(self) -> Dict[str, str]:
            """
            Requests channel metadata
            
            :params:
                user_input (str): user inputted string
                youtube (googlapiclient.discovery.Resource): authenticated api client
            :return: channel metadata as dict. Keys of dict:
                upload_playlist_ID (str): ID of Entire playlist uploaded on channel
                channel_name (str): Channel name
                channel_subscriber_count (str): total subscribers to channel 
                channel_video_count (str): total videos uploaded
                channel_start_date (str): date channel started
                channel_thumbnail_url (str): url to thumbnail - highest resolution
                channel_description (str): the description provided by the channel
            
            """
            channel_request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=self.channel_ID
                )
            channel_res = channel_request.execute()
            channel_details = channel_res['items'][0]
            channel_statistics = channel_details['statistics']
            channel_snippet = channel_details['snippet']

            channel_data = dict(
                    upload_playlist_ID = channel_details['contentDetails']['relatedPlaylists']['uploads'],
                    channel_name = channel_snippet['title'],
                    channel_subscriber_count = channel_statistics['subscriberCount'],
                    channel_video_count = channel_statistics['videoCount'],
                    channel_start_date = channel_snippet['publishedAt'],
                    channel_thumbnail_url = channel_snippet['thumbnails']['high']['url'],
                    channel_description = channel_snippet['description']
                    )
            return channel_data

    def get_video_data(self) -> pd.core.frame.DataFrame:
        """
        Returns video information for a YouTube channel

        :return:
            df (pandas.core.frame.DataFrame): all videos in channel and data
        """
        channel_data = self.get_channel_data()
        channel_video_count = channel_data['channel_video_count']
        upload_playlist_ID = channel_data['upload_playlist_ID']
        
        video_response = []
        next_page_token = None
        while True:
            # obtaining video ID + titles
            playlist_request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    maxResults=50, # API Limit is 50
                    pageToken=next_page_token,
                    playlistId=upload_playlist_ID,
                    )
            playlist_response = playlist_request.execute()
            # isolating video ID
            vid_subset = [ vid_ID['contentDetails']['videoId'] for vid_ID in playlist_response['items'] ]
            # retrieving video statistics 
            vid_info_subset_request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=vid_subset
                )
            vid_info_subset_response = vid_info_subset_request.execute()
            video_response.append(vid_info_subset_response)
            # obtaining page token
            next_page_token = playlist_response.get('nextPageToken') # get method used because token may not exist
            if next_page_token is None:
                break

        df = pd.json_normalize(video_response, 'items')
        return df

    def main():
        return

if __name__ == '__main__':
    main()
