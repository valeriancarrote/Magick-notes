import dearpygui.dearpygui as dpg #yeah that many requerement
import json 
import base64
import pyperclip
from os import walk
import pyclip
from io import BytesIO
import win32clipboard
from PIL import Image
from copy_sub import ClipboardHistoryManager
import time 
import os
from popup import NotificationManager
from icon_recuperation import IconCache
import traceback
import sys
import ftfy

try:
    Icon = IconCache()
    notif = NotificationManager()       

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


    def delete_element_by_id(target_id):
        # We take the id from the json file and we delete the block
        with open("history_clipboard.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        original_length = len(data.get("history", []))
        data["history"] = [item for item in data["history"] if item.get("id") != target_id]
        new_length = len(data.get("history", []))

        if original_length == new_length:
            print(f"No element with id {target_id} was found.")
        else:
            print(f"Element with id {target_id} deleted.")

        with open("history_clipboard.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    files_dir = []
    def list_files_in_folder(folder_path):

        files_dir.clear()
        for item in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item)
            if os.path.isfile(full_path):
                files_dir.append(ftfy.fix_text(full_path))
        return files_dir  

    def do_things_with_json(): 
        global list_of_copy
        list_of_copy.clear()
        with open('history_clipboard.json', 'r') as file:
            list_of_copy = json.load(file)
        dpg.create_context()
    list_of_copy = []
    def supprimer_image(sender, app_data, user_data): 
        #print("User data c'est ca : ", user_data)
        if user_data.startswith("row_img_"):
            try:
                filename = user_data.split("_")[2]  
                filepath = os.path.join("image", filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
                    print(f"Fichier supprimé : {filepath}")
                    notif.show_notification("Image deleted ! ", 3, "info")
            except Exception as e:
                print(f"Erreur :  {e}")
                notif.show_notification(f"The image could not be deleted : {e} ", 3, "alert")
        if dpg.does_item_exist(user_data):

            dpg.delete_item(user_data)
    def supprimer_file(sender, app_data, user_data): 
        do_things_with_json()
        tag_row = user_data[0]
        id_fichier = user_data[2]
        essais = 0
        for x in list_of_copy["history"]: 
            if x["id"] == id_fichier: 
                path_file = x["content"] 
                path_file = ftfy.fix_text(path_file)
                name_of_the_file = os.path.basename(path_file)
                print(name_of_the_file)
                list_files_in_folder("files")
                print(files_dir)
                for x in files_dir:  
                    if name_of_the_file in x: 
                        os.remove(f"files/{name_of_the_file}")
                        delete_element_by_id(id_fichier)
                        print(f"the file {name_of_the_file} was deleted")
                        notif.show_notification(f"The file {name_of_the_file} was deleted ", 3, "info")
                        if dpg.does_item_exist(tag_row):

                            dpg.delete_item(tag_row)
                            return
                    if name_of_the_file not in x : 
                        essais += 1
                        if len(files_dir) == essais :   
                            print(f"The file {name_of_the_file} was not found")
                            notif.show_notification(f"There was an error during the suppresion of the file {name_of_the_file}", 3, "alert")
                            
    def supprimer_texte(sender, app_data, user_data): 
        truc_de_ligne = user_data[0]
        print(f"le truc de la ligne c'est ca :  {truc_de_ligne}")
        id_du_text_josn = user_data[2]
        print(f"l'id du json c'est ca :  {id_du_text_josn}")
        dpg.delete_item(truc_de_ligne)
        delete_element_by_id(id_du_text_josn)
    
    def on_resize(sender, app_data, user_data):
        width, height =  dpg.get_item_rect_size("IA")
        dpg.configure_item("input_text_id", width=width, height=height)

    def ask_ia(sender, app_data, user_data):

        with dpg.window(label="IA answer", tag="IA", width=300, height=200):
            dpg.add_loading_indicator(circle_count=10, radius=10, tag="loading_barrrrrr")
            from g4f.client import Client
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
            dpg.delete_item("loading_barrrrrr")
            dpg.add_input_text(default_value=rep_ia, multiline=True, width=300, height=200, tag="input_text_id")
            with dpg.item_handler_registry(tag="resize_handler"):
                dpg.add_item_resize_handler(callback=on_resize, user_data=None)
            dpg.bind_item_handler_registry("IA", "resize_handler")

    def open_file(sender, app_data, user_data): 


        id_fichier = user_data[2]
        for x in list_of_copy["history"]: 
            if x["id"] == id_fichier: 
                path_file = x["content"] 
                path_file = ftfy.fix_text(path_file)
                name_of_the_file = os.path.basename(path_file)
                print(name_of_the_file)
                list_files_in_folder("files")
                found = False
                for x in files_dir: 
                    if name_of_the_file in x: 
                        os.startfile(f"files\{name_of_the_file}")
                        found = True 
                        break
                if not found: 
                    print(f"File '{name_of_the_file}' not found.")
                    notif.show_notification(f"Can't open file {name_of_the_file}", 3, "alert")
    def button_callback(sender, app_data, user_data):

        texte = dpg.get_value(user_data)
        print(f"Copié : {texte}")
        pyperclip.copy(texte)
    def file_copy_to_cliboard(sender, app_data, user_data): 
        id_fichier = user_data
        for x in list_of_copy["history"]: 
            if x["id"] == id_fichier: 
                path_file = x["content"] 
                name_of_the_file = os.path.basename(path_file)
                print(name_of_the_file)
                list_files_in_folder("files")
                found = False
                for x in files_dir: 
                    if name_of_the_file in x: 
                        found = True
                        #os.startfile(f"files\{name_of_the_file}")
                        path = f"files\{name_of_the_file}" 
                        print(path)
                        command = f"powershell Set-Clipboard -LiteralPath {path}" 
                        os.system(command)
                        break
                if not found: 
                    print(f"File '{name_of_the_file}' not found.")

    def image_callback(sender, app_data, user_data):
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
    open_icon = load_icon("Icon\dossier.png")
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
            dpg.add_image_button(texture_tag=copy_icon, width=40, height=40, callback=image_callback, user_data=image_tag)
            dpg.add_image_button(texture_tag=deltet_icon, width=40, height=40, callback=supprimer_image, user_data=row_tag)

    def eceoutsdf(): 
        instance = ClipboardHistoryManager()

        instance.add_new_entry()
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
        children = dpg.get_item_children("files_tab", 1)
        if children:    
            for child in children:
                dpg.delete_item(child)
        number_tag_texte = 0
        number_tag_file = 0 

        for text in list_of_copy["history"]:
            number_tag_texte = number_tag_texte + 1
            if text["type"] == "Texte":
                    
                bas_no = text["content"]
                id_jssson = text["id"] 
                #print(f"l'id du json {id_jssson}")
                bas__yes = base64.b64decode(bas_no.encode()).decode()
                #print(bas__yes)
                add_table(bas__yes, number_tag_texte, id_jssson, "text") 
        for text in list_of_copy["history"]: 
            number_tag_file = number_tag_file + 1
            if text["type"] == "Fichier":
                    
                pathhh = text["content"]
                id_jssson = text["id"] 
                add_table(pathhh, number_tag_file, id_jssson, "file")            

    def add_table(texte, number, json_iidddd, type): 
        if type == str("text"): 
            row_tag = f"row_{number}_{int(time.time()*1000)}"
            
            with dpg.table_row(filter_key=f"{texte}", tag=row_tag, parent=filter_table_id):
                text_tag = f"text_{number}"
                dpg.add_text(texte, tag=text_tag, wrap=400)
                dpg.add_image_button(texture_tag=copy_icon, width=40, height=40, callback=button_callback, user_data=json_iidddd)
                dpg.add_image_button(texture_tag=deltet_icon, width=40, height=40, callback=supprimer_texte, user_data=[row_tag, number,json_iidddd])
                with dpg.group(horizontal=True):
                    input_tag = f"fun_{number}"
                    dpg.add_input_text(width=120, tag=input_tag)
                    dpg.add_button(label="Ask", callback=ask_ia, user_data=[text_tag, input_tag])
        if type == str("file"): 
            row_tag = f"row_{number}_{int(time.time()*1000)}"
            with dpg.table_row(tag=row_tag, parent="files_tab"):

                file_icon_texture = Icon.get_texture_for_file(texte)

                text_tag = f"file_{number}"
                
                with dpg.group(horizontal=True):
                    
                    dpg.add_image(file_icon_texture, width=30, height=30)
                    dpg.add_text(os.path.basename(ftfy.fix_text(texte)), tag=text_tag, wrap=400)
                dpg.add_image_button(texture_tag=copy_icon, width=40, height=40, callback=file_copy_to_cliboard, user_data=text_tag)
                dpg.add_image_button(texture_tag=deltet_icon, width=40, height=40, callback=supprimer_file, user_data=[row_tag, number,json_iidddd])
                dpg.add_image_button(texture_tag=open_icon, width=40, height=40, callback=open_file, user_data=[row_tag, number,json_iidddd])

    with dpg.font_registry():
        default_font = dpg.add_font("OpenSans.ttf", 15)
        with dpg.font("OpenSans.ttf", 15) as default_font: 
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_chars([0x201d, 0x2019, 0x2005, 0x201c, 0x153, 0x2022, 0x1f4cb, 0x274c])

    with dpg.window(label="Tutorial", tag="Tutorial"):
        with dpg.menu_bar():
            with dpg.menu(label="Tools"):
                dpg.add_menu_item(label="Show About", callback=lambda:dpg.show_tool(dpg.mvTool_About))
                dpg.add_menu_item(label="Show Metrics", callback=lambda:dpg.show_tool(dpg.mvTool_Metrics))
                dpg.add_menu_item(label="Show Documentation", callback=lambda:dpg.show_tool(dpg.mvTool_Doc))
                dpg.add_menu_item(label="Show Debug", callback=lambda:dpg.show_tool(dpg.mvTool_Debug))
                dpg.add_menu_item(label="Show Style Editor", callback=lambda:dpg.show_tool(dpg.mvTool_Style))
                dpg.add_menu_item(label="Show Font Manager", callback=lambda:dpg.show_tool(dpg.mvTool_Font))
                dpg.add_menu_item(label="Show Item Registry", callback=lambda:dpg.show_tool(dpg.mvTool_ItemRegistry))
                dpg.add_menu_item(label="Show Stack Tool", callback=lambda:dpg.show_tool(dpg.mvTool_Stack))

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
            with dpg.tab(label='Texte '):
                
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
                                #print(bas__yes)
                                add_table(bas__yes, number_tag, id_jssson, "text" )
            with dpg.tab(label='Image'):
                    with dpg.table(header_row=True, no_host_extendX=True, delay_search=True,
                        borders_innerH=True, borders_outerH=True, borders_innerV=True,
                        borders_outerV=True, context_menu_in_body=True, row_background=True,
                        height=300, scrollY=True, tag="image_tab") as table_id:
                        dpg.add_table_column(label="Image", init_width_or_weight=0.3) 
                        dpg.add_table_column(label="Copy", init_width_or_weight=0.3)
                        dpg.add_table_column(label="Delete", init_width_or_weight=0.3) 
                        tag_number = 0
                        for x in list_images:
                            tag_number = x
                            add_images(x, tag_number)
            with dpg.tab(label='Files '):
                #dpg.add_text("This feature is in developement, this should not work very well...")
                with dpg.table(header_row=True, no_host_extendX=True, delay_search=True,
                        borders_innerH=True, borders_outerH=True, borders_innerV=True,
                        borders_outerV=True, context_menu_in_body=True, row_background=True,
                        height=300, scrollY=True, tag="files_tab") as table_id:
                        dpg.add_table_column(label="Files", init_width_or_weight=0.3) 
                        dpg.add_table_column(label="Copy", init_width_or_weight=0.3)
                        dpg.add_table_column(label="Delete", init_width_or_weight=0.3)
                        dpg.add_table_column(label="Open", init_width_or_weight=0.3) 
                        number_tag = 10000000
                        for i in list_of_copy["history"]:
                            number_tag = number_tag + 1
                            if i["type"] == "Fichier": 
                                pathh = i["content"]
                                id_jsson = i["id"] 
                                add_table(pathh, number_tag, id_jsson, "file")






        dpg.bind_font(default_font)
    
    dpg.create_viewport(title='Remember Copy', width=800, height=500, large_icon="Icon/icon.ico")
    dpg.set_viewport_large_icon("Icon/icon.ico")
    dpg.set_viewport_small_icon("Icon/icon.ico")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Tutorial", True)

    create_texture_registry()
    dpg.start_dearpygui()
    dpg.destroy_context()
except Exception:
    with open("startup_error_log.txt", "w") as f:
        f.write(traceback.format_exc())
    sys.exit(1)