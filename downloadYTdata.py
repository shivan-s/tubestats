#!usr/bin/env python3
# downloadYTdata.py - Downloads youtube video data using the YouTube API, saves accessing API all the time
# by Shivan Sivakumaran


import os
import requests
import math

import pandas as pd

import googleapiclient.discovery
import googleapiclient.errors

from dotenv import load_dotenv

def download_video_data(channel_ID):

    load_dotenv()

    # loading API creds
    api_service_name = 'youtube'
    api_version = 'v3'
    youtube = googleapiclient.discovery.build(api_service_name, api_version,
                                             developerKey=os.getenv('YT_API_KEY'))

    # looking into channel
    channel_request = youtube.channels().list(
        part='snippet,contentDetails',
        id=channel_ID
        )
    channel_res = channel_request.execute()
    print(channel_res)
    # accessing list of videos
    upload_playlist_ID = channel_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # accesses list 50 videos at a time
    def playlist_requester(pageToken=None,upload_playlist_ID=upload_playlist_ID):
        playlist_request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            maxResults=50,
            pageToken=pageToken,
            playlistId=upload_playlist_ID
        )
        playlist_res = playlist_request.execute()

        return playlist_res

    playlist_res = playlist_requester()

    TOTAL_UPLOADS = playlist_res['pageInfo']['totalResults'] # total videos in upload playslist
    next_page_token = playlist_res['nextPageToken'] # needed to access the next page

    list_video_IDs = [ video_ID['contentDetails']['videoId'] for video_ID in playlist_res['items'] ] # first 50
    
    # download information from all videos
    while TOTAL_UPLOADS > len(list_video_IDs):
        nextpage_playlist_res = playlist_requester(next_page_token)
        list_video_IDs.extend([ video_ID['contentDetails']['videoId'] for video_ID in nextpage_playlist_res['items']
                                if video_ID['contentDetails']['videoId'] not in list_video_IDs ]) # using .extend() vs .append()
        if 'nextPageToken' in nextpage_playlist_res:
            next_page_token = nextpage_playlist_res['nextPageToken'] # if there no more pages this tag does not exist

        print('Number of Uploaded Videos: ' + str(len(list_video_IDs)))

    video_response = [ youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=list_video_IDs[50*i:50*(i+1)]
        ).execute() for i in range(math.ceil(len(list_video_IDs)/50)) ]

    # save to dataframe and then to .csv file
    df = pd.json_normalize(video_response, 'items')
    
    #csv_file_name = str(channel_res['items'][0]['snippet']['customUrl'] + 'video_data.csv')
    csv_file_name = 'video_data.csv'
    df.to_csv(csv_file_name, index=False)
    print('Saved.')


if __name__ == '__main__':
    return
