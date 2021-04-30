#!/usr/bin/env python3
# tubestats/youtube_presenter.py - main script for displaying data and graphs
#
# by Shivan Sivakumaran

from datetime import datetime, timedelta

import streamlit as st

from tubestats.youtube_data import YouTubeData

# @st.cache
def fetch_data(channel_id):
        youtuber_data = YouTubeData(channel_id)
        return youtuber_data
    
def main():

    ALI_ABDAAL_CHANNEL_ID = 'UCoOae5nYA7VqaXzerajD0lg'
    DEBUG = True

    st.title('TubeStats Analysis of a YouTube Channel')
    """
    *by Shivan Sivakumaran 2021*
    ## Introduction
    This page provides a brief analysis of a YouTube Channel.
    """

    channel_id = st.text_input('Please enter Youtube channel ID:', ALI_ABDAAL_CHANNEL_ID)
    if not channel_id:
        st.warning('Please input a Youtube channel ID (e.g. %s)' % ALI_ABDAAL_CHANNEL_ID)
        st.stop()
    youtuber_data = fetch_data(channel_id) 
    if DEBUG == True:
        raw_df = youtuber_data.raw_dataframe()
        st.write(raw_df)

    df = youtuber_data.dataframe()
    
    st.header(youtuber_data.channel_name())
    st.image(youtuber_data.thumbnail_url(), width=400)
    st.write(youtuber_data.channel_description())

    st.header('Quick Statistics')
    st.markdown('Total Number of Videos: `' + '{:,}'.format(int(youtuber_data.video_count())) + '`')
    st.markdown('Join Date: `' + str(youtuber_data.start_date()) + '`')
    st.markdown('Total View Count:  `' + '{:,}'.format(int(youtuber_data.total_channel_views())) + '`')
    st.markdown('Total Comments: `' + '{:,}'.format(int(youtuber_data.total_comments())) + '`')
    st.markdown('Total Watch Time: `' + str(youtuber_data.total_watchtime()) + '`')

    st.subheader('Videos')
    """
    List of videos and all relevant features.
    """
    st.write(df)
    """
    Below is a graph plotting the views of each video over time. The colour represents the like and dislike, the size represents the number of views.
    """
    first_video_date = df['snippet.publishedAt_REFORMATED'].min().to_pydatetime()
    last_video_date = df['snippet.publishedAt_REFORMATED'].max().to_pydatetime()
    
    def date_slider(date_end=datetime.today()):
        date_start, date_end = st.slider(
                'Date range to include',
                min_value=first_video_date, # first video
                max_value=last_video_date, #value for date_end
                value=(first_video_date , last_video_date), #same as min value
                step=timedelta(days=2),
                format='YYYY-MM-DD',
                key=999)
        return date_start, date_end
  
    date_start, date_end = date_slider()

    transformed_df = youtuber_data.transform_dataframe(date_start=date_start, date_end=date_end) 
    
    c = youtuber_data.scatter_all_videos(transformed_df)
    st.altair_chart(c, use_container_width=True)

    def display_vid_links(most_viewed_info):
            st.write('Here are links to the videos:')
            titles = most_viewed_info['title']
            links = most_viewed_info['link']
            for i in range(len(titles)):
                title = str(titles[i])
                link = 'https://www.youtube.com/watch?v=' + str(links[i])
                if i == 0:
                    st.write(str(i+1) + '. ' + title)
                    st.video(data=link)
                else:
                    st.markdown(str(i+1) + '. ' + '[' + title +']' + '(' + link + ')')

    st.subheader('Most Popular Videos')
    """
    Hypothesis: view count indicates well performing videos. The content is engaging enough and liked to be recommended and viewed more often to other viewers.
    """
    most_viewed_info = youtuber_data.most_viewed_videos(df=transformed_df)
    st.write(most_viewed_info['preserved_df'])
    display_vid_links(most_viewed_info)

    #dislike_num = st.slider('Number of videos', 5, 20, key=0)
    st.subheader('Most Unpopular Videos')
    """
    Remaining a hypothesis, people actively show their digust for a video by hitting dislike video. Hence, we are provided with a like-dislike ratio. We also have the sum to ensure we have enough likes/dislikes for fair comparison.
    """
    most_disliked_info = youtuber_data.most_disliked_videos(df=transformed_df)
    st.write(most_disliked_info['preserved_df'])
    display_vid_links(most_disliked_info)        

    st.subheader('Videos by time difference')
    time_df = youtuber_data.time_difference_calculate(df=transformed_df)
    time_diff = youtuber_data.list_time_difference_ranked(df=time_df)
    st.write(time_diff)
    st.write(youtuber_data.time_difference_plot(df=time_df), use_container_width=True)

    # TODO: provide statistics for time difference
    # TODO: list previous and next video after video with greatest difference 
    prev_col, great_col, next_col = st.beta_columns(3)
    vid_list = youtuber_data.greatest_time_difference_video(time_df)
    with prev_col:
        st.subheader('Previous:')
        st.video('https://www.youtube.com/watch?v=' + str(vid_list['prev']))
    with great_col:
        st.subheader('Greatest:')
        st.video('https://www.youtube.com/watch?v=' + str(vid_list['greatest']))
    with next_col:
        st.subheader('Next:')
        st.video('https://www.youtube.com/watch?v=' + str(vid_list['_next']))


if __name__ == '__main__':
    main()
