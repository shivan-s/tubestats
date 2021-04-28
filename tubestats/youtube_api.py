#!usr/bin/env python3
# tubestats/youtube_api_connect.py  - connects to YouTube API
#                                   - authenticates API_LIMIT
#                                   - downloads data based on channel ID
#                                   - returns pandas dataframe
#
# by Shivan Sivakumaran

import os
import math
import logging
from typing import Dict

from dotenv import load_dotenv
import pandas as pd
import googleapiclient.discovery
import googleapiclient.errors

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
    def __init__(self, channel_ID: str):
        self.channel_ID = channel_ID
        self.youtube = create_api()

    def get_channel_data(self) -> Dict[str, str]:
            """
            Requests channel metadata
            
            :params:
                channel_ID (str): YouTube Channel ID
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

        :params:
            channel_data (Dict[str, str]): this is outputted from the function get_channel_data
        :return:
            df (pandas.core.frame.DataFrame): all videos in channel and data
        """
        channel_data = self.get_channel_data()
        channel_video_count = channel_data['channel_video_count']
        upload_playlist_ID = channel_data['upload_playlist_ID']
        
        def playlist_requester(pageToken=None,upload_playlist_ID=upload_playlist_ID):
            API_LIMIT = 50 # YouTube API limit
            playlist_request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    maxResults=API_LIMIT,
                    pageToken=pageToken,
                    playlistId=upload_playlist_ID,
                    )
            playlist_res = playlist_request.execute()
            return playlist_res
        
        total_page_requests = math.ceil(int(channel_video_count)/50)
        next_page_token = None

        list_vid_ID= []
        for i in range(total_page_requests):
            playlist_res = playlist_requester(next_page_token)
            vid_subset = [ vid_ID['contentDetails']['videoId'] for vid_ID in playlist_res['items'] ]            
            list_vid_ID.extend(vid_subset)
            logging.info('Number of Uploaded Videos: ' + str(len(list_vid_ID)))
            if i < total_page_requests-1:
                next_page_token = playlist_res['nextPageToken']

        video_response = []
        for i in range(total_page_requests):
            video_res_subset = self.youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=list_vid_ID[50*i:50*(i+1)]
            ).execute()
            video_response.append(video_res_subset)

        df = pd.json_normalize(video_response, 'items')

        return df

def main():
    return

if __name__ == '__main__':
    main()
