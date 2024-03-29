"""TubeStats."""
import os
from datetime import datetime, timedelta

import sentry_sdk
import streamlit as st
from data import YouTubeData

sentry_sdk.init(
    dsn=f"https://{os.getenv('SENTRY_DSN', '')}.ingest.sentry.io/6629324",
    traces_sample_rate=0.1,
)

# Settings
ALI_ABDAAL_CHANNEL_ID = "UCoOae5nYA7VqaXzerajD0lg"
SHIVAN_SIVAKUMARAN_CHANNEL_ID = "UCrbYXWUmeCy4GqArthu4hCw"
DEBUG = False
DEFAULT_CHANNEL_ID = SHIVAN_SIVAKUMARAN_CHANNEL_ID


@st.cache
def fetch_data(user_input):
    youtuber_data = YouTubeData(user_input)
    return youtuber_data


def main():
    """Entry point."""
    """
    # TubeStats
    *Analysis for YouTube Channel Consistency*

    [Source code](https://github.com/shivan-s/tubestats)
    """
    # User input
    user_input = st.text_input(
        "Please enter YouTube channel ID or URL to a YouTube video:",
        DEFAULT_CHANNEL_ID,
    )
    if not user_input:
        st.warning(
            f"Please input a YouTube channel ID (e.g. {DEFAULT_CHANNEL_ID}) or a link to a YouTube video."
        )
        st.stop()
    youtuber_data = fetch_data(user_input)

    if DEBUG is True:
        raw_df = youtuber_data.raw_dataframe()
        st.write(raw_df)

    df = youtuber_data.dataframe()

    st.header(youtuber_data.channel_name())
    img_col, stat_col = st.columns(2)
    with img_col:
        st.image(youtuber_data.thumbnail_url())
    with stat_col:
        st.subheader("Quick Statistics")
        st.markdown(
            "Total Number of Videos: `"
            + "{:,}".format(int(youtuber_data.video_count()))
            + "`"
        )
        st.markdown("Join Date: `" + str(youtuber_data.start_date()) + "`")
        st.markdown(
            "Total View Count:  `"
            + "{:,}".format(int(youtuber_data.total_channel_views()))
            + "`"
        )
        st.markdown(
            "Total Comments: `"
            + "{:,}".format(int(youtuber_data.total_comments()))
            + "`"
        )
        st.markdown(
            "Total Watch Time: `" + str(youtuber_data.total_watchtime()) + "`"
        )
    st.write(youtuber_data.channel_description())

    st.header("Videos")
    """
    Below is a graph plotting the views of each video over time. Please note:
    - colour represents the like
    - size represents the number of views.
    - a natural log axis is applied to the view count due to its 'viral' nature
    """
    first_video_date = (
        df["snippet.publishedAt_REFORMATED"].min().to_pydatetime()
    )
    last_video_date = (
        df["snippet.publishedAt_REFORMATED"].max().to_pydatetime()
    )

    def date_slider(date_end=datetime.today()):
        date_start, date_end = st.slider(
            "Select date range to include:",
            min_value=first_video_date,  # first video
            max_value=last_video_date,  # value for date_end
            value=(first_video_date, last_video_date),  # same as min value
            step=timedelta(days=2),
            format="YYYY-MM-DD",
            key=999,
        )
        return date_start, date_end

    date_start, date_end = date_slider()
    transformed_df = youtuber_data.transform_dataframe(
        date_start=date_start, date_end=date_end
    )
    c = youtuber_data.scatter_all_videos(transformed_df)
    st.altair_chart(c, use_container_width=True)

    st.subheader("Videos by Time Difference")
    """
    This looks at the time difference between the current video and the previous video.
    """
    time_df = youtuber_data.time_difference_calculate(df=transformed_df)
    time_diff = youtuber_data.list_time_difference_ranked(df=time_df)
    st.altair_chart(
        youtuber_data.time_difference_plot(df=time_df),
        use_container_width=True,
    )

    quantiles = youtuber_data.time_difference_statistics(df=time_df)
    st.subheader("Time Difference Statistics:")
    st.markdown(
        "25th Percentile: `" + "{:0.1f}".format(quantiles[0.25]) + "` days"
    )
    st.markdown("Median: `" + "{:0.1f}".format(quantiles[0.50]) + "` days")
    st.markdown(
        "75th Percentile: `" + "{:0.1f}".format(quantiles[0.75]) + "` days"
    )
    st.markdown(
        "Longest Hiatus: `" + "{:0.1f}".format(quantiles[1.0]) + "` days"
    )

    vid_list = youtuber_data.greatest_time_difference_video(time_df)
    st.subheader("Longest Hiatus:")
    st.video("https://www.youtube.com/watch?v=" + str(vid_list["greatest"]))
    prev_col, next_col = st.columns(2)
    with prev_col:
        st.subheader("Previous:")
        st.video("https://www.youtube.com/watch?v=" + str(vid_list["prev"]))
    with next_col:
        st.subheader("Next:")
        st.video("https://www.youtube.com/watch?v=" + str(vid_list["_next"]))
    st.write(time_diff)

    def display_vid_links(most_viewed_info):
        st.write("Here are links to the videos:")
        titles = most_viewed_info["title"]
        links = most_viewed_info["link"]
        for i in range(len(titles)):
            title = str(titles[i])
            link = "https://www.youtube.com/watch?v=" + str(links[i])
            if i == 0:
                st.write(str(i + 1) + ". " + title)
                st.video(data=link)
            else:
                st.markdown(
                    str(i + 1) + ". " + "[" + title + "]" + "(" + link + ")"
                )

    st.header("Most Popular Videos")
    """
    Hypothesis: view count indicates well performing videos. \
            The content is engaging enough and liked to be \
            recommended and viewed more often to other viewers.
    """
    most_viewed_info = youtuber_data.most_viewed_videos(df=transformed_df)
    st.write(most_viewed_info["preserved_df"])
    display_vid_links(most_viewed_info)

    st.header("List of Video")
    """
    List of videos and all relevant features.
    """
    st.write(df)


if __name__ == "__main__":
    st.set_page_config(page_title="TubeStats")
    if DEBUG == True:
        main()
    try:
        main()
    except Exception as e:
        st.error("Error: {e}".format(e=e))
