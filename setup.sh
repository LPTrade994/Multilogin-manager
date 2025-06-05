#!/bin/bash
mkdir -p ~/.streamlit/
cat <<EOF > ~/.streamlit/config.toml
[server]
headless = true
port = $PORT
enableCORS = false

[theme]
primaryColor = '#FF4B4B'
backgroundColor = '#FFFFFF'
secondaryBackgroundColor = '#F0F2F6'
textColor = '#262730'
font = 'sans serif'
EOF
