#!usr/bin/env python3
# functions.py - contains all the functions and calculations for analysing Ali Abdaal's youtube channel
# For Shivan: Up tp part where time difference display

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import math
import isodate

from datetime import date, time, datetime, timedelta

def load_YT_data():
    filepath = 'video_data.csv'
    return pd.read_csv(filepath)

class YT_functions:
    '''
    contains all methods needed to create output
    '''

    def __init__(self, filepath='video_data.csv'):
        self.filepath = filepath

    def load_data(self):
        self.df = pd.read_csv(self.filepath)

    def transformed_data(self):
        # keeping relevant columns
        self.df = self.df[['snippet.publishedAt',
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
        self.df = self.df.astype({'statistics.viewCount': 'int',
            'statistics.likeCount': 'int',
            'statistics.dislikeCount': 'int'})

        # creating like-dislike ratio and sum of likes and dislikes ratio
        self.df['statistics.sum-like-dislike'] = self.df['statistics.likeCount'] + self.df['statistics.dislikeCount']
        self.df['statistics.like-dislike-ratio'] = self.df['statistics.likeCount'].div((self.df['statistics.dislikeCount']+self.df['statistics.likeCount']), axis=0)

        # applying natural log to view count as data is tail heavy
        self.df['statistics.viewCount_NLOG'] = self.df['statistics.viewCount'].apply(lambda x : np.log(x))

        # reformatting time data
        # Turning ISO8061 into duation that python can utilise
        self.df['snippet.publishedAt_REFORMATED'] = self.df['snippet.publishedAt'].apply(lambda x : datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
        self.df['contentDetails.duration_REFORMATED'] = self.df['contentDetails.duration'].apply(lambda x : isodate.parse_duration(x)) 
    # sorting data by time
        self.df = self.df.sort_values(by='snippet.publishedAt_REFORMATED')
        
        return self.df

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
        return self.df[param_id[stat_type]].sum()

    def total_videos(self):
        return len(self.df)

    def max_views(self):
        return max(list(self.df['statistics.viewCount_NLOG'].values))

    def scatter_all_videos(self, views, ratio):
        df_views = self.df[(self.df['statistics.viewCount_NLOG']>=views) & (self.df['statistics.like-dislike-ratio']>=ratio)]
        c = alt.Chart(df_views, title='Plot of videos over time').mark_point().encode(
                x=alt.X('snippet\.publishedAt_REFORMATED:T', axis=alt.Axis(title='Date Published')),
                y=alt.Y('statistics\.viewCount_NLOG:Q', axis=alt.Axis(title='Natural Log of Views')),
                color=alt.Color('statistics\.like-dislike-ratio:Q', scale=alt.Scale(scheme='turbo'), legend=None),
                tooltip=['snippet\.title:N', 'statistics\.viewCount:Q', 'statistics\.like-dislike-ratio:Q'],
                size=alt.Size('statistics\.viewCount:Q', legend=None)
        )
        return c

    def snip_dates(self, cutoff_time=datetime(2017, 6, 1)):
        """
        cutoff_time: (datetime) e.g  datetime(2017, 6, 1))
        """
        self.df = self.df[self.df['snippet.publishedAt_REFORMATED']>cutoff_time]

    def disliked_videos(self, num=5):
        """
        num: (int) e.g. 5
        """
        return self.df.sort_values(by='statistics.like-dislike-ratio')[['snippet.title', 
                                                    'statistics.like-dislike-ratio',
                                                    'statistics.viewCount', 
                                                    'statistics.sum-like-dislike']].head(int(num))

    def most_disliked_video(self, num):
        most_disliked_id = self.df.sort_values(by='statistics.like-dislike-ratio')[['snippet.title', 'id']]
        title = str(most_disliked_id['snippet.title'].values[num])
        link = 'https://www.youtube.com/watch?v=' + str(most_disliked_id['id'].values[num])
        return title, link

    def viewed_videos(self, num=5):
        """
        num: (int) e.g. 5
        """
        return self.df.sort_values(by='statistics.viewCount', ascending=False)[['snippet.title',
                                                            'statistics.viewCount',
                                                            'statistics.like-dislike-ratio']].head(int(num))

    def most_viewed_video(self, num):
        most_viewed_id = self.df.sort_values(by='statistics.viewCount', ascending=False)[['snippet.title', 'id']]
        title = str(most_viewed_id['snippet.title'].values[num])
        link = 'https://www.youtube.com/watch?v=' + str(most_viewed_id['id'].values[num])
        return title, link

    def time_difference_calculate(self):

        video_dates = dict(zip(self.df.index, self.df['snippet.publishedAt_REFORMATED']))
        video_diff = video_dates.copy() # duplicating dict .copy() so memory isn't referenced

        for i in video_dates.keys():
            if i == max(list(video_dates.keys())):
                td = video_dates[i]- video_dates[i]
            else:
                td = video_dates[i] - video_dates[i+1]

            video_diff[i] = td.days + ( td.seconds / 60 / 60 / 24 )

        td_df = pd.DataFrame(data=video_diff.values(), index=video_diff.keys(), columns=['snippet.time_diff'])
        self.df = pd.concat([self.df, td_df], axis=1)
        return self.df
    
    def list_time_difference_ranked(self, num=10):
        return self.df.sort_values(by='snippet.time_diff', ascending=False)[['snippet.time_diff', 
            'snippet.publishedAt_REFORMATED', 'snippet.title']].head(int(num))
        
    def jitter_plot(self):
        c1 = alt.Chart(self.df, title='Time Difference',).mark_circle().encode(
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
            )#.configure_facet(
             #   spacing=0
            #).configure_view(
            #    stroke=None
            #)
        c2 = alt.Chart(self.df).mark_bar().encode(
                x=alt.X('snippet\.time_diff:Q', title='Day from previous video', bin=alt.Bin(maxbins=22)),
                y='count()',
                tooltip='count()'
                )
        c = c1
        return c


