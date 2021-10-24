#!usr/bin/env python3
# tubestats/youtube_data.py - wrangles data acquired from tubestats/youtube_api.py
#                           - produces channel and video statistics
#                           - produces graphs based on channel and video channel_statistics
# by Shivan Sivakumaran

import math
import logging
import re
from datetime import date, datetime, timedelta
from typing import List, Dict

import isodate
import pandas as pd
import numpy as np
import altair as alt

from tubestats.youtube_api import YouTubeAPI


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
        name = self.channel_data["channel_name"]
        return name

    def video_count(self) -> int:
        """
        Provies total video count of the channel

        :params: self
        :return: count
        :rtype: int
        """
        count = int(self.channel_data["channel_video_count"])
        return count

    def start_date(self) -> str:
        """
        Provides a start date for the YouTube channel

        :params: self
        :return: date channel started
        :rtype: str
        """
        channel_start_date = self.channel_data["channel_start_date"]
        # removes time as provides decimal seconds, also time not relevant
        r = re.compile(r"(T.*)")
        channel_start_date = r.sub("T", channel_start_date)  # type: ignore
        date_converted = datetime.strptime(channel_start_date, "%Y-%m-%dT")  # type: ignore
        date_converted = date_converted.strftime("%d %B %Y")  # type: ignore
        return date_converted  # type: ignore

    def thumbnail_url(self) -> str:
        """
        Provides URL to high quality channel thumbnail

        :params: self
        :return: url link
        :rtype: str
        """
        thumb = self.channel_data["channel_thumbnail_url"]
        return thumb

    def channel_description(self) -> str:
        """
        Returns channel description

        :params: self
        :return: channel description
        :rtype: str
        """
        description = self.channel_data["channel_description"]
        return description

    def raw_dataframe(self) -> pd.core.frame.DataFrame:
        """
        Return raw data frame of video data for channel

        :params: self
        :return: raw_df
        :rtype: pandas.core.frame.DataFrame
        """
        raw_df = self.df
        return raw_df

    def dataframe(self) -> pd.core.frame.DataFrame:
        """
        Returns dataframe with relevant columns and altering the datatypes

        :params: self
        :return: df
        :rtype: pandas.core.frame.DataFrame
        """
        # TODO: Check performance

        df = self.df
        df = df[
            [
                "snippet.publishedAt",
                "snippet.title",
                "id",
                "snippet.description",
                "contentDetails.duration",
                "statistics.viewCount",
                "statistics.likeCount",
                "statistics.dislikeCount",
                "statistics.favoriteCount",
                "statistics.commentCount",
            ]
        ]

        # turns nan into 0s
        df = df.fillna(0)

        # changing dtypes
        df = df.astype(
            {
                "statistics.viewCount": "int",
                "statistics.likeCount": "int",
                "statistics.dislikeCount": "int",
                "statistics.commentCount": "int",
            }
        )

        # creating like-dislike ratio and sum of likes and dislikes ratio
        df["statistics.sum-like-dislike"] = (
            df["statistics.likeCount"] + df["statistics.dislikeCount"]
        )
        df["statistics.like-dislike-ratio"] = df["statistics.likeCount"].div(
            (df["statistics.dislikeCount"] + df["statistics.likeCount"]),
            axis=0,
        )

        # reformatting time data
        # Turning ISO8061 into duation that python can utilise
        df["snippet.publishedAt_REFORMATED"] = df["snippet.publishedAt"].apply(
            lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
        )
        df["contentDetails.duration_REFORMATED"] = df[
            "contentDetails.duration"
        ].apply(lambda x: isodate.parse_duration(x))
        # sorting data by time
        df = df.sort_values(
            by="snippet.publishedAt_REFORMATED", ascending=True
        )
        return df

    def total_channel_views(self) -> int:
        """
        Return the total channel views

        :params: self
        :returns: total channel views
        :rtype: numpy.int64
        """
        df = self.dataframe()
        view_total = df["statistics.viewCount"].sum()
        return view_total

    def total_watchtime(self) -> timedelta:
        """
        Returns total view times for all videos of the channel

        :params: self
        :returns: watchtime_total
        :rtype: timedelta
        """
        df = self.dataframe()
        watchtime_total = df["contentDetails.duration_REFORMATED"].sum()
        return watchtime_total

    def total_comments(self) -> int:
        """
        Returns total comments throughout the whole channel

        :params: self
        :returns: commments_total
        :rtype: numpy.int64
        """
        df = self.dataframe()
        comments_total = df["statistics.commentCount"].sum()
        return comments_total

    def transform_dataframe(
        self, date_start: datetime, date_end: datetime
    ) -> pd.core.frame.DataFrame:
        """
        Constrains video between two dates

        :params: self
            date_start: (datetime)
            date_end: (datetime)
        :return: df
        :rtype: pandas.core.frame.DataFrame
        """
        df = self.dataframe()
        df = df[
            (df["snippet.publishedAt_REFORMATED"] >= date_start)
            & (df["snippet.publishedAt_REFORMATED"] < date_end)
        ]
        return df

    def scatter_all_videos(
        self, df: pd.core.frame.DataFrame
    ) -> alt.vegalite.v4.Chart:
        """
        Produces graph plotting natural log of views over

        :params: self
            df: (dataframe)
        :return: c (altair.vegalite.v4.Chart)
        """
        df_views = df
        c = (
            alt.Chart(df_views, title="Plot of videos over time")
            .mark_point()
            .encode(
                x=alt.X(
                    "snippet\.publishedAt_REFORMATED:T",
                    axis=alt.Axis(title="Date Published"),
                ),
                y=alt.Y(
                    "statistics\.viewCount:Q",
                    axis=alt.Axis(title="View Count"),
                    scale=alt.Scale(type="log"),
                ),
                color=alt.Color(
                    "statistics\.like-dislike-ratio:Q",
                    scale=alt.Scale(scheme="turbo"),
                    legend=None,
                ),
                tooltip=[
                    "snippet\.title:N",
                    "statistics\.viewCount:Q",
                    "statistics\.like-dislike-ratio:Q",
                ],
                size=alt.Size("statistics\.viewCount:Q", legend=None),
            )
        )
        return c

    def most_viewed_videos(
        self, df: pd.core.frame.DataFrame, num: int = 10
    ) -> dict:
        """
        Returns dictionary for dataframe, title of video, and video link in a dictionary, ranking most viewed videos

        :params: self
            df (dataframe)
            num (int): default is 10
        :return: key for dictionary:
            'preserved_df' (dataframe)
            'title' (str): video titles
            'link' (str): url links to video
        """
        # sort df and then keep relevant tags
        sorted_df = df.sort_values(by="statistics.viewCount", ascending=False)
        title = list(sorted_df["snippet.title"].values[0:num])
        link = list(sorted_df["id"].values[0:num])
        preserved_df = sorted_df[
            [
                "snippet.title",
                "statistics.viewCount",
                "statistics.like-dislike-ratio",
            ]
        ].head(int(num))
        most_viewed_info = dict(
            preserved_df=preserved_df,
            title=title,
            link=link,
        )
        return most_viewed_info

    def most_disliked_videos(
        self, df: pd.core.frame.DataFrame, num: int = 5
    ) -> dict:
        """
        Returns dictionary for dataframe, title of video, and video link in a dictionary ranking most disliked videos

        :params: self
            df (dataframe)
            num (int): default is 5
        :return: key for dictionary:
            'preserved_df' (dataframe)
            'title' (str): video titles
            'link' (str): url links to video
        """
        # sort df and then keep relevant tags
        sorted_df = df.sort_values(
            by="statistics.like-dislike-ratio", ascending=True
        )
        title = list(sorted_df["snippet.title"].values[0:num])
        link = list(sorted_df["id"].values[0:num])
        preserved_df = sorted_df[
            [
                "snippet.title",
                "statistics.like-dislike-ratio",
                "statistics.viewCount",
                "statistics.sum-like-dislike",
            ]
        ].head(int(num))

        most_disliked_info = dict(
            preserved_df=preserved_df,
            title=title,
            link=link,
        )
        return most_disliked_info

    def time_difference_calculate(
        self, df: pd.core.frame.DataFrame
    ) -> pd.core.frame.DataFrame:
        """
        Works out time difference between videos

        :params: self
            df (pandas.core.frame.DataFrame): video information
        :return: dataframe with time difference
        :rtype: pandas.core.frame.DataFrame
        """
        video_dates = dict(zip(df.index, df["snippet.publishedAt_REFORMATED"]))
        video_diff = (
            video_dates.copy()
        )  # duplicating dict .copy() so memory isn't referenced

        for i in video_dates.keys():
            if i == max(list(video_dates.keys())):
                td = video_dates[i] - video_dates[i]
            else:
                td = video_dates[i] - video_dates[i + 1]

            video_diff[i] = td.days + (td.seconds / 60 / 60 / 24)

        td_df = pd.DataFrame(
            data=video_diff.values(),
            index=video_diff.keys(),
            columns=["snippet.time_diff"],
        )
        new_df = pd.concat([df, td_df], axis=1)
        return new_df

    def list_time_difference_ranked(
        self, df: pd.core.frame.DataFrame, num: int = 10
    ) -> pd.core.frame.DataFrame:
        """
        Provides a list of videos ranked by time difference (day from previous video)
        :params: self
            df (pandas.core.frame.DataFrame)
        :return: time_differences
        :rtype: pandas.core.frame.DataFrame
        """
        time_differences = df.sort_values(
            by="snippet.time_diff", ascending=False
        )[
            [
                "snippet.time_diff",
                "snippet.publishedAt_REFORMATED",
                "snippet.title",
                "id",
            ]
        ].head(
            int(num)
        )
        return time_differences

    def time_difference_plot(
        self, df: pd.core.frame.DataFrame
    ) -> alt.vegalite.v4.Chart:
        """
        Provides a 'dotplot' of videos based on length of time from previous video

        :params: self
            df (pandas.core.frame.DataFrame)
        :return:
            c - graph
        :rtype: altair.vegalite.v4.Chart
        """
        c = (
            alt.Chart(
                df,
                title="Time Difference",
            )
            .mark_circle()
            .encode(
                y=alt.Y(
                    "jitter:Q",
                    title=None,
                    axis=alt.Axis(
                        values=[0], ticks=True, grid=False, labels=False
                    ),
                    scale=alt.Scale(),
                ),
                x=alt.X(
                    "snippet\.time_diff:Q", title="Day from previous video"
                ),
                color=alt.Color("statistics\.viewCount:Q", legend=None),
                tooltip=["snippet\.title:N", "statistics\.viewCount:Q"],
            )
            .transform_calculate(
                jitter="sqrt(-2*log(random()))*cos(2*PI*random())"
            )
            .configure_facet(spacing=0)
            .configure_view(stroke=None)
        )
        return c

    def time_difference_statistics(
        self, df: pd.core.frame.DataFrame
    ) -> Dict[float, float]:
        """
        Gives quantiles for time differences

        :params: self
            df (pandas.core.frame.DataFrame)
        :return: time_diff_quantiles
        :rtype: dict
        """
        time_diff_quantiles = dict(
            df["snippet.time_diff"].quantile([0.25, 0.50, 0.75, 1.0])
        )
        return time_diff_quantiles

    def greatest_time_difference_video(
        self, df: pd.core.frame.DataFrame
    ) -> Dict[str, str]:
        """
        Provides the video id with the greatest time difference, the previous and the next video as a dict

        :params: self
            df (pandas.core.frame.DataFrame) - df ordered by index, time differences and with dates slected
        :return: vid_list with keys:
            'greatest' - id with greatest time diff
            'prev' - id previous
            '_next' - id next
        :rtype: Dict[str, str]
        """
        # video with greatest difference
        # multply by -1 because dataframe is reversed
        vid_list = dict(
            greatest=df.iloc[df["snippet.time_diff"].idxmax() * -1]["id"],
            prev=df.iloc[df["snippet.time_diff"].idxmax() * -1 + 1]["id"],
            _next=df.iloc[df["snippet.time_diff"].idxmax() * -1 - 1]["id"],
        )
        return vid_list


def main():
    return


if __name__ == "__main__":
    main()
