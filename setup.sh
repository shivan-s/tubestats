#!/bin/sh

#mkdir -p ./.streamlit
#echo "[server]\n
#headless = true\n
#port = $PORT\n
#enableCORS = false
#" > ./.streamlit/config.toml
streamlit run ./youtube_presenter.py
