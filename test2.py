import dearpygui.dearpygui as dpg
from PIL import Image
import os
import time

# Function to get images from the image folder
def get_images_from_folder():
    """Get all image files from the 'image' folder"""
    image_folder = "image"
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    if not os.path.exists(image_folder):
        print(f"Warning: '{image_folder}' folder doesn't exist!")
        return []
    
    image_files = []
    try:
        for filename in os.listdir(image_folder):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_files.append(filename)
        
        if not image_files:
            print(f"No image files found in '{image_folder}' folder!")
        else:
            print(f"Found {len(image_files)} images: {image_files}")
            
    except Exception as e:
        print(f"Error reading image folder: {e}")
    
    return image_files

def create_bento_layout_test(image_list, parent_tag):
    """
    Test version of bento layout
    """
    # Analyze image dimensions
    image_info = []
    for img in image_list:
        try:
            img_path = f"image/{img}"
            with Image.open(img_path) as pil_img:
                width, height = pil_img.size
                aspect_ratio = width / height
                
                # Categorize and size images
                if aspect_ratio > 1.5:  # Wide
                    display_width = 250
                    display_height = int(250 / aspect_ratio)
                elif aspect_ratio < 0.7:  # Tall
                    display_width = int(180 * aspect_ratio)
                    display_height = 180
                else:  # Square-ish
                    display_width = 120
                    display_height = 120
                
                image_info.append({
                    'filename': img,
                    'width': display_width,
                    'height': display_height,
                    'aspect_ratio': aspect_ratio
                })
        except Exception as e:
            print(f"Error with {img}: {e}")

    # Create masonry columns
    num_columns = 3
    columns = [[] for _ in range(num_columns)]
    column_heights = [0] * num_columns

    # Distribute images
    for img_info in image_info:
        shortest_col = column_heights.index(min(column_heights))
        columns[shortest_col].append(img_info)
        column_heights[shortest_col] += img_info['height'] + 10

    # Create the layout
    with dpg.group(horizontal=True, parent=parent_tag):
        for col_idx, column in enumerate(columns):
            with dpg.group(horizontal=False):
                dpg.add_text(f"Column {col_idx + 1}", color=(255, 255, 0))
                for img_info in column:
                    add_test_image(img_info)

def add_test_image(img_info):
    """Add a test image with popup"""
    try:
        img_path = f"image/{img_info['filename']}"
        width, height, channels, data = dpg.load_image(img_path)
        
        with dpg.texture_registry():
            texture_id = dpg.add_static_texture(width, height, data)
        
        dpg.add_spacer(height=5)
        
        # Create image button
        img_btn_tag = f"img_btn_{img_info['filename']}_{int(time.time()*1000)}"
        img_btn = dpg.add_image_button(
            texture_id, 
            width=img_info['width'], 
            height=img_info['height'], 
            tag=img_btn_tag
        )
        
        # Add popup
        popup_tag = f"popup_{img_info['filename']}_{int(time.time()*1000)}"
        with dpg.popup(img_btn, tag=popup_tag):
            dpg.add_text(f"Image: {img_info['filename']}")
            dpg.add_text(f"Size: {img_info['width']}x{img_info['height']}")
            dpg.add_text(f"Aspect: {img_info['aspect_ratio']:.2f}")
            dpg.add_button(label="Test Action", callback=lambda: print(f"Clicked {img_info['filename']}"))
            
    except Exception as e:
        print(f"Error adding image {img_info['filename']}: {e}")

def refresh_layout():

    children = dpg.get_item_children("bento_container", 1)
    if children:
        for child in children:
            dpg.delete_item(child)
    
    # Recreate layout with images from image folder
    image_files = get_images_from_folder()
    if image_files:
        create_bento_layout_test(image_files, "bento_container")
    else:
        dpg.add_text("No images found in 'image' folder!", parent="bento_container", color=(255, 100, 100))

# Main application
def main():
    dpg.create_context()
    
    image_files = get_images_from_folder()
    
    with dpg.window(label="Bento Layout Test", tag="main_window"):
        
        with dpg.child_window(tag="bento_container", autosize_x=True, height=400, horizontal_scrollbar=True):
            create_bento_layout_test(image_files, "bento_container")

    dpg.create_viewport(title='Bento Layout Test', width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()