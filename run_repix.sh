#!/bin/bash

# Activate virtual environment if you're using one
# source /path/to/your/venv/bin/activate  # Uncomment and modify if needed

# Navigate to the app directory
cd "$(dirname "$0")"

# Run the Streamlit app
streamlit run src/streamlit_app.py 