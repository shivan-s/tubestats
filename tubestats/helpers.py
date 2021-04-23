#!usr/bin/env python
# tubestats/helpers.py - contains helper functions for tubestates/main.py
#                      - authenticates API
#                      - downloads data for channel
#                      - contains functions for displaying graphs/data on tubestats/main.py
# by Shivan Sivakumaran

import os
import math
import logging
import re
from pathlib import Path
from datetime import date, time, datetime, timedelta

import requests
from dotenv import load_dotenv
import isodate
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import googleapiclient.discovery
import googleapiclient.errors

#TODO: time difference graph
#TODO: fix axis for the videos x log of view count graph

def create_api():
    """
    Used to authenticate YouTube API
    """
    load_dotenv()
    api_service_name = 'youtube'
    api_version = 'v3'
    youtube = googleapiclient.discovery.build(api_service_name,
            api_version,
            developerKey=os.getenv('YT_API_KEY'))
    return youtube

class VideoData():
    """
    Downloads data from a channel
    channel_id: (str) this is a channel id for the Youtube Channel in quesion
    """
    def __init__(self, channel_ID):
        self.channel_ID = channel_ID
        self.youtube = create_api()
        self.BASE_DIR = Path(__file__).parent.parent

    def get_channel_data(self):
        """
        Requests channel metadata
        no input
        returns dictionary
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

    def get_video_data(self):
        """
        Returns pandas dataframe of all videos in channel
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
        # df.to_hdf(self.BASE_DIR / 'data' / 'store_tube.h5', key=self.channel_ID)

        return df
    
    def load_video_data(self):
        """
        (defunct) Loads YouTube data - instead of having to access the API all the time
        """
        # df = pd.read_hdf(self.BASE_DIR / 'data' / 'store_tube.h5', key=self.channel_ID)
        return # df

class DataFunctions:
    '''
    contains all methods needed to create output
    '''

    def __init__(self, channel_ID):
        self.channel_ID = channel_ID
        video_data = VideoData(self.channel_ID)
        self.channel_data = video_data.get_channel_data() 
        self.df = video_data.get_video_data()
        
    def channel_name(self):
        name = self.channel_data['channel_name']
        return name

    def video_count(self):
        count = int(self.channel_data['channel_video_count'])
        return count

    def start_date(self):
        channel_start_date = self.channel_data['channel_start_date']
         # removes time as provides decimal seconds, also time not relevant
        r = re.compile(r'(T.*)')
        channel_start_date = r.sub('T', channel_start_date)
        date_converted = datetime.strptime(channel_start_date, '%Y-%m-%dT')
        date_converted = date_converted.strftime('%d %B %Y')
        return date_converted

    def thumbnail_url(self):
        thumb = self.channel_data['channel_thumbnail_url']
        return thumb

    def channel_description(self):
        description = self.channel_data['channel_description']
        return description

    def dataframe(self):
        """
        Returns dataframe with relevant columns and altering the datatypes
        """
        df = self.df
        df = df[['snippet.publishedAt',
            'snippet.title',
            'id',
            'snippet.description',
            'snippet.tags', 
           'contentDetails.duration',
            'statistics.viewCount',
            'statistics.likeCount',
            'statistics.dislikeCount',
            'statistics.favoriteCount',
            'statistics.commentCount']]
        
        # changing dtypes
        df = df.astype({'statistics.viewCount': 'int',
            'statistics.likeCount': 'int',
            'statistics.dislikeCount': 'int',
            'statistics.commentCount': 'int',})

        # creating like-dislike ratio and sum of likes and dislikes ratio
        df['statistics.sum-like-dislike'] = df['statistics.likeCount'] + df['statistics.dislikeCount']
        df['statistics.like-dislike-ratio'] = df['statistics.likeCount'].div((df['statistics.dislikeCount']+df['statistics.likeCount']), axis=0)

        # applying natural log to view count as data is tail heavy
        df['statistics.viewCount_NLOG'] = df['statistics.viewCount'].apply(lambda x : np.log(x))

        # reformatting time data
        # Turning ISO8061 into duation that python can utilise
        df['snippet.publishedAt_REFORMATED'] = df['snippet.publishedAt'].apply(lambda x : datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
        df['contentDetails.duration_REFORMATED'] = df['contentDetails.duration'].apply(lambda x : isodate.parse_duration(x)) 
        # sorting data by time
        df = df.sort_values(by='snippet.publishedAt_REFORMATED', ascending=True)
        
        return df

    def total_stat(self, stat_type='view'):
        """
        stat_type: (str) options can be 
        'view' - total views, 
        'watchtime' - total watch time, 
        'comment' - total comments.
        """
        stat_type = str(stat_type)
        param_id = { 'view': 'statistics.viewCount',
                'watchtime': 'contentDetails.duration_REFORMATED',
                'comment': 'statistics.commentCount'}
        df = self.dataframe()
        total = df[param_id[stat_type]].sum()
        return total

    def transform_dataframe(self, date_start, date_end):
        """
        Constrains data to date_start and date_end
        date_start: (datetime)
        date_end: (datetime)
        """
        df = self.dataframe()
        df = df[(df['snippet.publishedAt_REFORMATED']>=date_start) & (df['snippet.publishedAt_REFORMATED']<date_end)]
        return df

    def scatter_all_videos(self, df):
        """
        Produces graph plotting natural log of views over
        df: (dataframe) 
        """
        df_views = df
        c = alt.Chart(df_views, title='Plot of videos over time').mark_point().encode(
                x=alt.X('snippet\.publishedAt_REFORMATED:T', axis=alt.Axis(title='Date Published')),
                y=alt.Y('statistics\.viewCount_NLOG:Q', axis=alt.Axis(title='Natural Log of Views')),
                color=alt.Color('statistics\.like-dislike-ratio:Q', scale=alt.Scale(scheme='turbo'), legend=None),
                tooltip=['snippet\.title:N', 'statistics\.viewCount:Q', 'statistics\.like-dislike-ratio:Q'],
                size=alt.Size('statistics\.viewCount:Q', legend=None)
        )
        return c

    def most_viewed_videos(self, df, num: int = 10):
        """
        Returns dataframe, title of video, and video link in tuple
        df: (dataframe)
        num: (int) e.g. 10
        """
        # sort df and then keep relevant tags
        sorted_df = df.sort_values(by='statistics.viewCount', ascending=False)
        title = list(sorted_df['snippet.title'].values[0:num])
        link = list(sorted_df['id'].values[0:num])
        preserved_df = sorted_df[[
             'snippet.title',
             'statistics.viewCount',
             'statistics.like-dislike-ratio',
             ]].head(int(num))
        most_viewed_info = dict(
                preserved_df=preserved_df,
                title=title,
                link=link,
                )
        return most_viewed_info

    def most_disliked_videos(self, df, num=5):
        """
        Disliked - Returns dataframe, title of video, and video link in tuple
        df: (dataframe)
        num: (int) e.g. 5
        """
        # sort df and then keep relevant tags
        sorted_df = df.sort_values(by='statistics.like-dislike-ratio', ascending=True)
        title = list(sorted_df['snippet.title'].values[0:num])
        link = list(sorted_df['id'].values[0:num])
        preserved_df = sorted_df[[
            'snippet.title', 
            'statistics.like-dislike-ratio',
            'statistics.viewCount', 
            'statistics.sum-like-dislike']].head(int(num))

        most_disliked_info = dict(
                preserved_df=preserved_df,
                title=title,
                link=link,
                )
        return most_disliked_info

#TODO: plot time difference data

    def time_difference_calculate(self, df):
        """
        Works out time difference between videos
        """
        video_dates = dict(zip(df.index, df['snippet.publishedAt_REFORMATED']))
        video_diff = video_dates.copy() # duplicating dict .copy() so memory isn't referenced

        for i in video_dates.keys():
            if i == max(list(video_dates.keys())):
                td = video_dates[i]- video_dates[i]
            else:
                td = video_dates[i] - video_dates[i+1]

            video_diff[i] = td.days + ( td.seconds / 60 / 60 / 24 )

        td_df = pd.DataFrame(data=video_diff.values(), index=video_diff.keys(), columns=['snippet.time_diff'])
        new_df = pd.concat([df, td_df], axis=1)
        return new_df
    
    def list_time_difference_ranked(self, df, num=10):
        time_differences = df.sort_values(by='snippet.time_diff', ascending=False)[[
            'snippet.time_diff',
            'snippet.publishedAt_REFORMATED',
            'snippet.title'
            ]].head(int(num))
        return time_differences
        
    def get_time_difference_plot(self, df):
        c1 = alt.Chart(df, title='Time Difference',).mark_circle().encode(
            y=alt.Y(
                'jitter:Q',
                title=None,
                axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False),
                scale=alt.Scale(),
                ),
            x=alt.X('snippet\.time_diff:Q', title='Day from previous video'),
            color=alt.Color('statistics\.viewCount:Q', legend=None),
            tooltip=['snippet\.title:N', 'statistics\.viewCount:Q'],
            ).transform_calculate(
                jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
            ).configure_facet(
                spacing=0
            ).configure_view(
                stroke=None
            )
        c2 = alt.Chart(df).mark_bar().encode(
                x=alt.X('snippet\.time_diff:Q', title='Day from previous video', bin=alt.Bin(maxbins=22)),
                y='count()',
                tooltip='count()'
                )
        c = c1
        return c


def main():
    return

if __name__ == '__main__':
    main()
