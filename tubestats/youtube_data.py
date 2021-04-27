#!usr/bin/env python
# tubestats/youtube_data.py - wrangles data acquired from tubestats/youtube_api.py
#                           - produces channel and video statistics
#                           - produces graphs based on channel and video channel_statistics
# by Shivan Sivakumaran

import math
import logging
import re
from datetime import date, datetime, timedelta

import isodate
import pandas as pd
import numpy as np
import altair as alt

from tubestats.youtube_api import YouTubeAPI

# TODO: write docstrings and test

class YouTubeData:
    """
    Class containing methods to apply statistics to YouTube channel
    :params:
        channel_ID (str): channel_ID
        channel_data (optional): used for testing
        df (optional): used for testing
    """
    def __init__(self, channel_ID: str, channel_data=None, df=None):
        self.channel_ID = channel_ID
        self.channel_data = channel_data
        self.df = df

        if self.channel_data is None or self.df is None:
            video_data = YouTubeAPI(channel_ID)
            self.channel_data = video_data.get_channel_data()
            self.df = video_data.get_video_data()
        
    def channel_name(self) -> str:
        """
        Provides the channel name
        :params: self
        :return: channel name
        :rtype: str
        
        """
        name = self.channel_data['channel_name']
        return name

    def video_count(self) -> int:
        """
        Provies total video count of the channel
        :params: self
        :return: count
        :rtype: int
        """
        count = int(self.channel_data['channel_video_count'])
        return count

    def start_date(self) -> str:
        """
        Provides a start date for the YouTube channel
        :params: self
        :return: date channel started
        :rtype: str
        """
        channel_start_date = self.channel_data['channel_start_date']
         # removes time as provides decimal seconds, also time not relevant
        r = re.compile(r'(T.*)')
        channel_start_date = r.sub('T', channel_start_date)
        date_converted = datetime.strptime(channel_start_date, '%Y-%m-%dT')
        date_converted = date_converted.strftime('%d %B %Y')
        return date_converted

    def thumbnail_url(self) -> str:
        """
        Provides URL to high quality channel thumbnail
        :params: self
        :return: url link
        :rtype: str
        """
        thumb = self.channel_data['channel_thumbnail_url']
        return thumb

    def channel_description(self) -> str:
        """
        Returns channel description
        :params: self
        :return: channel description
        :rtype: str
        """
        description = self.channel_data['channel_description']
        return description
    
    def raw_dataframe(self):
        """
        Return raw data frame of video data for channel
        :params: self
        :return: raw_df 
        :rtype: pandas.core.frame.DataFrame
        """
        raw_df = self.df
        return raw_df

    def dataframe(self):
        """
        Returns dataframe with relevant columns and altering the datatypes
        :params: self
        :return: df
        :rtype: pandas.core.frame.DataFrame
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

    def total_channel_views(self) -> int:
        """
        Return the total channel views
        :params: self
        :returns: total channel views
        :rtype: numpy.int64
        """
        df = self.dataframe()
        view_total = df['statistics.viewCount'].sum()
        return view_total

    def total_watchtime(self) -> timedelta:
        """
        Returns total view times for all videos of the channel
        :params: self
        :returns: watchtime_total
        :rtype: timedelta
        """        
        df = self.dataframe()
        watchtime_total = df['contentDetails.duration_REFORMATED'].sum()
        return watchtime_total

    def total_comments(self) -> int:
        """
        Returns total comments throughout the whole channel
        :params: self
        :returns: commments_total
        :rtype: numpy.int64
        """
        df = self.dataframe()
        comments_total = df['statistics.commentCount'].sum()
        return comments_total

    def transform_dataframe(self, date_start: datetime, date_end: datetime):
        """
        Constrains video between two dates
        :params: self
            date_start: (datetime)
            date_end: (datetime)
        :return: df
        :rtype: pandas.core.frame.DataFrame
        """
        df = self.dataframe()
        df = df[(df['snippet.publishedAt_REFORMATED']>=date_start) & (df['snippet.publishedAt_REFORMATED']<date_end)]
        return df

    def scatter_all_videos(self, df):
        """
        Produces graph plotting natural log of views over
        :params: self
            df: (dataframe)
        :return: c (
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
