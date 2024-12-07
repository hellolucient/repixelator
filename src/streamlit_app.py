import streamlit as st
from PIL import Image
import json
import io
import random
import time

st.set_page_config(
    page_title="Repix - NFT Image Generator",
    page_icon="🎨",
    layout="wide"
)

def shuffle_pixels(json_data):
    """Randomly redistribute pixels while maintaining the same colors"""
    pixels = json_data['pixels']
    coordinates = list(pixels.keys())
    colors = list(pixels.values())
    random.shuffle(colors)
    return {'pixels': dict(zip(coordinates, colors))}

def process_pixel_data(json_data, shuffled=False, modifications=None, cursor_pos=None):
    try:
        # First apply any pixel modifications
        pixels_data = json_data['pixels'].copy()
        if modifications:
            pixels_data.update(modifications)
        
        # Create a new json_data with the modifications
        modified_json = {'pixels': pixels_data}
        
        # If shuffled, randomize all pixels including modifications
        if shuffled:
            modified_json = shuffle_pixels(modified_json)
        
        # Calculate dimensions
        pixels_data = modified_json['pixels']
        max_x = max(int(coord.split(',')[0]) for coord in pixels_data.keys())
        max_y = max(int(coord.split(',')[1]) for coord in pixels_data.keys())
        width = max_x + 1
        height = max_y + 1
        
        scale_factor = min(2000 // width, 2000 // height)
        final_width = width * scale_factor
        final_height = height * scale_factor
        
        img = Image.new('RGB', (final_width, final_height), color='black')
        pixels = img.load()
        
        # Draw all pixels
        for coord, color in pixels_data.items():
            x, y = map(int, coord.split(','))
            for dx in range(scale_factor):
                for dy in range(scale_factor):
                    pixels[x * scale_factor + dx, y * scale_factor + dy] = tuple(color)
        
        # Draw cursor (make it more visible)
        if cursor_pos:
            cursor_x, cursor_y = cursor_pos
            cursor_coord = f"{cursor_x},{cursor_y}"
            # Only draw cursor if this pixel hasn't been modified
            if cursor_coord not in modifications and 0 <= cursor_x <= max_x and 0 <= cursor_y <= max_y:
                border_thickness = max(2, scale_factor // 8)
                cursor_color = (255, 0, 0)  # Bright red
                
                # Draw border
                for dx in range(scale_factor):
                    for dy in range(scale_factor):
                        # Top and bottom borders
                        if dy < border_thickness or dy >= scale_factor - border_thickness:
                            x = cursor_x * scale_factor + dx
                            y = cursor_y * scale_factor + dy
                            if 0 <= x < final_width and 0 <= y < final_height:
                                pixels[x, y] = cursor_color
                        
                        # Left and right borders
                        if dx < border_thickness or dx >= scale_factor - border_thickness:
                            x = cursor_x * scale_factor + dx
                            y = cursor_y * scale_factor + dy
                            if 0 <= x < final_width and 0 <= y < final_height:
                                pixels[x, y] = cursor_color
        
        return img
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def main():
    st.title("🎨 Repix - NFT Image Generator")
    st.write("Transform your pixel data into high-resolution NFT images")
    
    # Initialize session states
    if 'modifications' not in st.session_state:
        st.session_state.modifications = {}
    if 'shuffled' not in st.session_state:
        st.session_state.shuffled = False
    if 'cursor_x' not in st.session_state:
        st.session_state.cursor_x = 0
    if 'cursor_y' not in st.session_state:
        st.session_state.cursor_y = 0
    
    # CSS for cursor controls
    st.markdown("""
        <style>
        .cursor-container button {
            padding: 0 !important;
            width: 32px !important;
            height: 32px !important;
            line-height: 1 !important;
            font-size: 20px !important;
        }
        .cursor-container div[data-testid="column"] {
            padding: 0 !important;
            margin: 0 !important;
        }
        .coord-text {
            text-align: center;
            line-height: 32px !important;
            font-size: 14px !important;
            padding: 0 8px !important;
        }
        .stButton:not(.cursor-container button) > button {
            width: auto !important;
            height: auto !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload your pixel data JSON files", 
        type="json",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Files")
            file_names = [f.name for f in uploaded_files]
            selected_file = st.selectbox(
                "Select a file to preview",
                file_names
            )
            
            st.subheader("Modify Pixels")
            cursor_container = st.container()
            with cursor_container:
                _, col_up, _ = st.columns([1,0.8,1])
                with col_up:
                    if st.button("⬆️", key="up"):
                        st.session_state.cursor_y = max(0, st.session_state.cursor_y - 1)
                
                col_left, col_center, col_right = st.columns([0.8,1,0.8])
                with col_left:
                    if st.button("⬅️", key="left"):
                        st.session_state.cursor_x = max(0, st.session_state.cursor_x - 1)
                with col_center:
                    st.markdown(f'<div class="coord-text">({st.session_state.cursor_x}, {st.session_state.cursor_y})</div>', unsafe_allow_html=True)
                with col_right:
                    if st.button("➡️", key="right"):
                        st.session_state.cursor_x += 1
                
                _, col_down, _ = st.columns([1,0.8,1])
                with col_down:
                    if st.button("⬇️", key="down"):
                        st.session_state.cursor_y += 1
            
            st.write("")
            
            with st.form("pixel_modification"):
                x_coord = st.number_input("X Coordinate", 
                                        min_value=0, 
                                        value=st.session_state.cursor_x, 
                                        step=1)
                y_coord = st.number_input("Y Coordinate", 
                                        min_value=0, 
                                        value=st.session_state.cursor_y, 
                                        step=1)
                color = st.color_picker("Pick a color", "#000000")
                rgb_color = [int(color[1:][i:i+2], 16) for i in (0, 2, 4)]
                
                if st.form_submit_button("Apply Pixel"):
                    coord_key = f"{x_coord},{y_coord}"
                    st.session_state.modifications[coord_key] = rgb_color
                    st.success(f"Modified pixel at ({x_coord}, {y_coord})")
            
            if st.button("Reset Modifications"):
                st.session_state.modifications = {}
            
            # Download section
            st.subheader("Download Images")
            images_to_download = st.multiselect(
                "Select images to download",
                options=file_names,
                default=None,
                key="download_selection"
            )
            
            if st.button("⬇️ Download Selected Images"):
                if not images_to_download:
                    st.warning("Please select at least one image to download")
                else:
                    with st.spinner("Processing selected images..."):
                        for file_name in images_to_download:
                            try:
                                file = next(f for f in uploaded_files if f.name == file_name)
                                file.seek(0)  # Reset file pointer
                                json_data = json.load(file)
                                img = process_pixel_data(json_data, modifications=st.session_state.modifications)
                                img_bytes = io.BytesIO()
                                img.save(img_bytes, format='PNG')
                                img_bytes.seek(0)
                                
                                st.download_button(
                                    label=f"Download {file_name}",
                                    data=img_bytes.getvalue(),
                                    file_name=f"repix_nft_{file_name}.png",
                                    mime="image/png",
                                    key=f"download_{file_name}"
                                )
                            except json.JSONDecodeError:
                                st.error(f"Invalid JSON format in file: {file_name}")
                            except Exception as e:
                                st.error(f"Error processing {file_name}: {str(e)}")
        
        with col2:
            st.subheader("Preview")
            selected_index = file_names.index(selected_file)
            file = uploaded_files[selected_index]
            
            try:
                col_buttons = st.columns(3)
                with col_buttons[0]:
                    if st.button("🎲 SHAKE"):
                        st.session_state.shuffled = True
                with col_buttons[1]:
                    if st.button("🏗️ BUILD"):
                        st.session_state.shuffled = False
                
                file.seek(0)  # Reset file pointer
                json_data = json.load(file)
                with st.spinner("✨ Generating preview..."):
                    img = process_pixel_data(
                        json_data, 
                        st.session_state.shuffled,
                        st.session_state.modifications,
                        cursor_pos=(st.session_state.cursor_x, st.session_state.cursor_y)
                    )
                    
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    st.image(img, caption=f"Preview: {file.name}", use_column_width=True)
                    
                    col2_1, col2_2 = st.columns([1, 2])
                    with col2_1:
                        st.download_button(
                            label="⬇️ Download This Image",
                            data=img_bytes.getvalue(),
                            file_name=f"repix_nft_{selected_index+1}.png",
                            mime="image/png"
                        )
                    with col2_2:
                        st.info(f"Image Size: {img.size[0]}x{img.size[1]} pixels")
                    
                    if st.session_state.modifications:
                        st.subheader("Current Modifications")
                        for coord, color in st.session_state.modifications.items():
                            st.write(f"Pixel at {coord}: RGB{tuple(color)}")
                    
            except json.JSONDecodeError:
                st.error(f"Invalid JSON format in file: {file.name}")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()