#!/bin/bash

# Start the Streamlit app with optimized Render configuration
streamlit run streamlit_app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.fileWatcherType=none \
  --server.enableWebsocketCompression=false \
  --browser.gatherUsageStats=false \
  --logger.level=info