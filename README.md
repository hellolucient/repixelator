# Repix - NFT Image Generator

A Streamlit web application that transforms pixel data into high-resolution NFT images.

## Features
- Upload multiple JSON pixel data files
- Preview and select individual images
- Generate high-resolution NFT images
- Download individual or all images at once
- Real-time preview with image size information
- Interactive pixel modification with cursor controls
- Shuffle pixels while maintaining color palette
- Reset modifications with a single click

## Installation & Running Locally

1. Clone the repository:
```bash
git clone https://github.com/hellolucient/repixelator.git
cd repixelator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run src/streamlit_app.py
```

## Input Format

The application expects JSON files with pixel data in the following format: