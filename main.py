import dearpygui.dearpygui as dpg #yeah that many requerement
import json 
import base64
import pyperclip
from os import walk
import pyclip
from io import BytesIO
import win32clipboard
from PIL import Image
import copy_sub
import time 
import os
from g4f.client import Client


def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()



list_images = []

mypath = "image/"
def do_things_with_image():
    global list_images
    list_images.clear()  
    for (dirpath, dirnames, filenames) in walk(mypath):
        list_images.extend(filenames)
        break

def do_things_with_json(): 
    global list_of_copy
    list_of_copy.clear()
    with open('history_clipboard.json', 'r') as file:
        list_of_copy = json.load(file)
    dpg.create_context()
list_of_copy = []
def supprimer_image(sender, app_data, user_data): 
    print("User data c'est ca : ", user_data)
    if user_data.startswith("row_img_"):
        try:
            filename = user_data.split("_")[2]  
            filepath = os.path.join("image", filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                
                print(f"Fichier supprimé : {filepath}")
        except Exception as e:
            print(f"Ya un errror :  {e}")
    if dpg.does_item_exist(user_data):

        dpg.delete_item(user_data)
    
def supprimer_texte(sender, app_data, user_data): 
    truc_de_ligne = user_data[0]
    print(f"le truc de la ligne c'est ca :  {truc_de_ligne}")
    id_du_text_josn = user_data[2]
    print(f"l'id du json c'est ca :  {id_du_text_josn}")
    dpg.delete_item(truc_de_ligne)
    with open('history_clipboard.json', 'r') as file:   
        data = json.load(file)

        for x in data["history"]: 
            if x["id"] == int(id_du_text_josn): 
                print("ca c'est cool")
                x['type'] = "Deleted"
    with open('history_clipboard.json', 'w') as file:
        json.dump(data, file, indent=4)  

def ask_ia(sender, app_data, user_data): 
    le_texte = user_data[0] 
    texte_input = user_data[1] 
    
    tetexte_inputt = dpg.get_value(texte_input)
    le_texte_du_texte = dpg.get_value(le_texte)
    print(f"le texte de l'input c'est ca : {tetexte_inputt} ")
    print(texte_input)
    print(f"le texte c'est ca : {le_texte_du_texte}")
    client = Client()
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"{tetexte_inputt} : {le_texte_du_texte}" }],
    )
    rep_ia = response.choices[0].message.content
    print(rep_ia)
    pyperclip.copy(rep_ia)


def button_callback(sender, app_data, user_data):
    texte = dpg.get_value(user_data)
    print(f"Copié : {texte}")
    pyperclip.copy(texte)

def image_callback(sender, app_data, user_data):
    print("ok")
    #print(user_data)
    filepath = f'image/{user_data}'
    image = Image.open(filepath)

    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    send_to_clipboard(win32clipboard.CF_DIB, data)

do_things_with_json()
do_things_with_image()

texture_registry = None


def load_icon(file_path):
    width, height, channels, data = dpg.load_image(file_path)
    with dpg.texture_registry():
        return dpg.add_static_texture(width, height, data)
copy_icon = load_icon("Icon\copier.png")
deltet_icon = load_icon("Icon\croix.png")
def create_texture_registry():
    global texture_registry
    if texture_registry is None:  
        with dpg.texture_registry() as registry:
            texture_registry = registry

def add_images(file_pathh, tag_number): 
    row_tag = f"row_img_{tag_number}_{int(time.time()*1000)}"
    image_tag = tag_number
    width, height, channels, data = dpg.load_image(f"image/{file_pathh}")
    with dpg.texture_registry():
        texture_id = dpg.add_static_texture(width, height, data)
    with dpg.table_row(tag=row_tag, parent="image_tab"):                 
        dpg.add_image(texture_id, width=200, height=200, tag=tag_number)
        dpg.add_button(label="copier", callback=image_callback, user_data=image_tag)
        dpg.add_button(label="supprimer", callback=supprimer_image, user_data=row_tag)

def eceoutsdf(): 
    copy_sub.execution()
    do_things_with_json()
    do_things_with_image()
    
    children = dpg.get_item_children("image_tab", 1)
    if children:
        for child in children:
            dpg.delete_item(child)

    create_texture_registry()

    if texture_registry:
        for item in dpg.get_item_children(texture_registry, slot=1):
            dpg.delete_item(item)

    for img in list_images:
        tag_number = img                         
        add_images(img, tag_number)
    children = dpg.get_item_children(filter_table_id, 1)
    if children:    
        for child in children:
            dpg.delete_item(child)
    number_tag = 0
    for text in list_of_copy["history"]:
        
        if text["type"] == "Texte":
            number_tag = number_tag + 1    
            bas_no = text["content"]
            id_jssson = text["id"] 
            #print(f"l'id du json {id_jssson}")
            bas__yes = base64.b64decode(bas_no.encode()).decode()
            #print(bas__yes)
            add_table(bas__yes, number_tag, id_jssson)


def add_table(texte, number, json_iidddd): 

    row_tag = f"row_{number}_{int(time.time()*1000)}"
    with dpg.table_row(filter_key=f"{texte}", tag=row_tag, parent=filter_table_id):
        text_tag = f"text_{number}"
        dpg.add_text(texte, tag=text_tag, wrap=400)
        dpg.add_image_button(texture_tag=copy_icon, width=40, height=40, callback=button_callback, user_data=text_tag)
        dpg.add_image_button(texture_tag=deltet_icon, width=40, height=40, callback=supprimer_texte, user_data=[row_tag, number,json_iidddd])
        with dpg.group(horizontal=True):
            input_tag = f"fun_{number}"
            dpg.add_input_text(width=120, tag=input_tag)
            dpg.add_button(label="Ask", callback=ask_ia, user_data=[text_tag, input_tag])


    

with dpg.font_registry():
    default_font = dpg.add_font("OpenSans.ttf", 15)
    with dpg.font("OpenSans.ttf", 15) as default_font: 
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_chars([0x201d, 0x2019, 0x2005, 0x201c, 0x153, 0x2022, 0x1f4cb, 0x274c])

with dpg.window(label="Tutorial", tag="Tutorial"):
    t2 = dpg.add_button(label="coucou", width=200, height=50, arrow=True, callback=eceoutsdf)

    with dpg.theme() as item_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (46, 240, 146))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (48, 255, 168))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (31, 163, 99))  
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 20, 10)

        dpg.bind_item_theme(t2, item_theme)
    with dpg.tab_bar(label='tabbar'):
        with dpg.tab(label='texte '):
            
            filter_table_id = dpg.generate_uuid()
            dpg.add_input_text(label="Chercher", user_data=filter_table_id, callback=lambda s, a, u: dpg.set_value(u, dpg.get_value(s)))
            with dpg.table(header_row=True, no_host_extendX=True, delay_search=True,
                borders_innerH=True, borders_outerH=True, borders_innerV=True,
                borders_outerV=True, context_menu_in_body=True, row_background=True,
                policy=dpg.mvTable_SizingFixedFit, height=300,
                scrollY=True, tag=filter_table_id) as table_id:
                dpg.add_table_column(label="Text") 
                dpg.add_table_column(label="Copy") 
                dpg.add_table_column(label="Delete") 
                dpg.add_table_column(label="Ask") 
                number_tag = 0
                for i in list_of_copy["history"]:
                     number_tag = number_tag + 1
                     if i["type"] == "Texte":
                            
                            bas_no = i["content"]
                            id_jssson = i["id"] 
                            bas__yes = base64.b64decode(bas_no.encode()).decode()
                            print(bas__yes)
                            add_table(bas__yes, number_tag, id_jssson)
        with dpg.tab(label='image'):
                with dpg.table(header_row=True, no_host_extendX=True, delay_search=True,
                    borders_innerH=True, borders_outerH=True, borders_innerV=True,
                    borders_outerV=True, context_menu_in_body=True, row_background=True,
                    height=300, scrollY=True, tag="image_tab") as table_id:
                    dpg.add_table_column(label="Image", init_width_or_weight=0.3) 
                    dpg.add_table_column(label="Copy", init_width_or_weight=0.3)
                    dpg.add_table_column(label="supre", init_width_or_weight=0.3) 
                    tag_number = 0
                    for x in list_images:
                        tag_number = x
                        add_images(x, tag_number)


    dpg.bind_font(default_font)

dpg.create_viewport(title='Remember Copy', width=800, height=500)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Tutorial", True)

create_texture_registry()
dpg.start_dearpygui()
dpg.destroy_context()