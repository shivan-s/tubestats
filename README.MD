# TubeStats

*By Shivan Sivakumaran*

Analysing YouTube channel consistency

## Introduction

This is a simple dashboard app, which analyses how consistent a YouTube channel is posting videos.

The inspiration for this project came from Ali Abdaal. Ali Abdaal preaches about consistency. So, the question is how consistent is Ali Abdaal at posting YouTube video. Also, we will look at some other interesting channel statistics.

[The app is live here](https://www.tubestats.app)

## Technologies used
- python 3.8
- `googleapiclient` to access YouTube data
- `pandas` and `NumPy` for data wrangling 
- `altair` for graphing
- `streamlit` to build the web interface 
- Heroku for hosting

## TODOs:
- [X] Minimal viable product LIVE
- [X] Refactor code
	- [X] split python files up
	- [X] type hinting
	- [X] Create test cases
- [X] Link to custom url: *https://www.tubestats.app*
- [ ] async
- [ ] Write a blog post about this topic

## Breaking down the script

- main script:
	- youtube_presenter.py - main script that presents information
- support scripts:
	- tubestats/youtube_api.py - helper script that connnects to API and downloads video data
	- tubestats/youtube_data.py - helper script that wrangles data and produces statstics and graphs
	- tubestats/youtube_parser.py - helper script that takes user inputs and produces a channel ID
	- tests/ - contain all test scripts and cases
- supporting files:
- Procfile - used by Heroku to set up environments
- setup.sh - used by Heroku to set up environments
- requirements.txt - contains dependancies for this project
- data/ - contains test data

## Feedback

Please [contact me](mailto:shivan@shivansivakumaran.com] if you have any questions.
