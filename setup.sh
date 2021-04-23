mkdir -p ~/.streamlit
echo "[sever]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml 
