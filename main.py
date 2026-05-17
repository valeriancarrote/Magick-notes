import dearpygui.dearpygui as dpg #yeah that many requerement
import json 
import base64
import pyperclip
from os import walk
from io import BytesIO
import win32clipboard
from PIL import Image
from copy_sub import ClipboardHistoryManager
import time 
import os
from popup import NotificationManager
from icon_recuperation import IconCache
import ftfy
import requests
from supabase import create_client
from dotenv import load_dotenv, dotenv_values , set_key
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs






Icon = IconCache()
notif = NotificationManager()       
supabase = create_client("https://dmmwwuatdanmcuxjnrsd.supabase.co", "sb_publishable_cMGonHxBVNbQrgQ1O7cilw_nOl9NcGB")

list_images = []
list_of_copy = []

captured_code = None  



def do_things_with_image():
    # make a list with all of the image 
    global list_images
    list_images.clear()  
    for (dirpath, dirnames, filenames) in walk("image/"):
        list_images.extend(filenames)
        break

def do_things_with_json(): 
    # converte the json into a list
    global list_of_copy
    list_of_copy.clear()
    with open('history_clipboard.json', 'r') as file:
        list_of_copy = json.load(file)
    dpg.create_context()

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
        print(f"Element with id {target_id} deleted form json file.")

    with open("history_clipboard.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def supprimer_image(sender, app_data, user_data): 
    # On supprime, l'image dans le fichier, l'id dans le json et l'image sur l'apli
    do_things_with_json()
    image_tag_aplli = user_data[0]
    tag_fichier = user_data[1]
    try: 
        
        for id in list_of_copy["history"]: 
            if id["content"] == int(tag_fichier.replace(".PNG", "")):   
                
                id_j = id["id"]
                delete_element_by_id(id_j)
        if dpg.does_item_exist(image_tag_aplli):
            dpg.delete_item(image_tag_aplli)
        os.remove(f"image/{tag_fichier}")
        notif.show_notification("Image deleted ! ", 3, "info")
    except Exception as e: 
        print(f"Erreur :  {e}")
        notif.show_notification(f"The image could not be deleted : {e} ", 3, "alert")

def supprimer_file(sender, app_data, user_data): 
    do_things_with_json()
    tag_row = user_data[0]
    id_fichier = user_data[2]
    for x in list_of_copy["history"]: 
        if x["id"] == id_fichier: 
            path_file = x["content"] 
            path_file = ftfy.fix_text(path_file)
            name_of_the_file = os.path.basename(path_file)
            try:
                os.remove(f"files/{name_of_the_file}")
                delete_element_by_id(id_fichier)
                print(f"the file {name_of_the_file} was deleted")
                notif.show_notification(f"The file {name_of_the_file} was deleted ", 3, "info")
                if dpg.does_item_exist(tag_row):

                    dpg.delete_item(tag_row)
                    return                
            except Exception:  
                print(f"The file {name_of_the_file} was not found")
                notif.show_notification(f"There was an error during the suppresion of the file {name_of_the_file}", 3, "alert")

def supprimer_texte(sender, app_data, user_data): 
    try : 
        truc_de_ligne = user_data[0]
        id_du_text_josn = user_data[2]    
        dpg.delete_item(truc_de_ligne)
        delete_element_by_id(id_du_text_josn)
        notif.show_notification(f"The texte was deleted ", 3, "info")
    except Exception: 
        print("The texte couldn't be deleted")


def on_resize(sender, app_data, user_data):
    width, height =  dpg.get_item_rect_size(user_data)
    dpg.configure_item("input_text_id", width=width, height=height)

def ask_ia(sender, app_data, user_data):
    tag_window = f"win_{int(time.time()*1000)}"
    with dpg.window(label="IA answer", tag=tag_window, width=300, height=200):
        tag_load = int(time.time()*1000)
        dpg.add_loading_indicator(circle_count=10, radius=10, tag=tag_load)
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
        dpg.delete_item(tag_load)
        dpg.add_input_text(default_value=rep_ia, multiline=True, width=300, height=200, tag="input_text_id")
        with dpg.item_handler_registry(tag="resize_handler"):
            dpg.add_item_resize_handler(callback=on_resize, user_data=tag_window)
        dpg.bind_item_handler_registry(tag_window, "resize_handler")

def open_file(sender, app_data, user_data): 
    id_fichier = user_data[2]
    for x in list_of_copy["history"]: 
        if x["id"] == id_fichier: 
            path_file = x["content"] 
            path_file = ftfy.fix_text(path_file)
            name_of_the_file = os.path.basename(path_file)
            print(name_of_the_file)
            try : 
                os.startfile(f"files\{name_of_the_file}")
            except Exception: 
                print(f"File '{name_of_the_file}' not found.")
                notif.show_notification(f"Can't open file {name_of_the_file}", 3, "alert")


def open_image(sender, app_data, user_data): 

    id_fichier = user_data
    print(id_fichier)
    try:
        os.startfile(f"image\{id_fichier}")
    except Exception as e: 
        print(f"Image '{id_fichier}' not found. Error : {e}")
        notif.show_notification(f"Can't open image {id_fichier}", 3, "alert")
def read_texte_in_image(sender, app_data, user_data): 
    tag_window = f"win_{int(time.time()*1000)}"
    with dpg.window(label="Text of the image", tag=tag_window, width=300, height=200):
        tag_load = int(time.time()*1000)
        dpg.add_loading_indicator(circle_count=10, radius=10, tag=tag_load)
        api_key = os.getenv("API_KEY_OCR")
            
        with open(f"image/{user_data}", 'rb') as image_file:
            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={'filename': image_file},
                data={
                    'apikey': api_key,
                    'language': 'auto',
                    'isOverlayRequired': False, 
                    'OCREngine' : 2
                }
            )
        
        result = response.json()
        if result.get("IsErroredOnProcessing"):
            print("Error:", result.get("ErrorMessage"))
        else:
            dpg.delete_item(tag_load)
            parsed_text = result['ParsedResults'][0]['ParsedText']
            pyperclip.copy(parsed_text)
            tag_texte = f"winnn_tqsd{int(time.time()*1000)}"
            dpg.add_input_text(default_value=parsed_text, multiline=True, width=300, height=200, tag=tag_texte)
            tag_winn = f"winnn_{int(time.time()*1000)}"
            with dpg.item_handler_registry(tag=tag_winn):
                dpg.add_item_resize_handler(callback=on_resize, user_data=tag_window)
            dpg.bind_item_handler_registry(tag_window, tag_winn)

                



def copy_texte(sender, app_data, user_data):
    
    texte = dpg.get_value(user_data)
    print(f"Copié : {texte}")
    pyperclip.copy(texte)
def file_copy_to_cliboard(sender, app_data, user_data): 
    id_fichier = user_data
    print(id_fichier)
    try: 
        for x in list_of_copy["history"]: 
            if x["id"] == id_fichier: 
                path_file = x["content"] 
                command = f"powershell Set-Clipboard -LiteralPath {path_file}" 
                os.system(command)
                notif.show_notification(f"File {path_file} copyed ", 3, "info")
    except Exception: 
        print(f"File '{user_data}' not found.")
        notif.show_notification(f"Can't copy file {path_file}", 3, "alert")
def copy_image(sender, app_data, user_data):
    filepath = f'image/{user_data}'
    image = Image.open(filepath)

    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

    notif.show_notification(f"The Image was succesfuly copied", 3, "info")


do_things_with_json()
do_things_with_image()

texture_registry = None


def load_icon(file_path):
    width, height, channels, data = dpg.load_image(file_path)
    with dpg.texture_registry():
        return dpg.add_static_texture(width, height, data)
copy_icon = load_icon("Icon/copier.png")
deltet_icon = load_icon("Icon/croix.png")
open_icon = load_icon("Icon/dossier.png")
icon_logged = load_icon("Icon/logged.png")
icon_not_logged = load_icon("Icon/not_logged.png")
icon_google = load_icon("Icon/google.png")

def create_texture_registry():
    global texture_registry
    if texture_registry is None:  
        with dpg.texture_registry() as registry:
            texture_registry = registry

def add_image_with_popup(file_pathh, tag_number, width=120, height=120):
    popup_btn_tag = f"{tag_number}_popup_{int(time.time()*1000)}"
    image_btn_tag = f"row_img_{tag_number}_btn_{int(time.time()*1000)}"

    width, height, channels, data = dpg.load_image(f"image/{file_pathh}")
    with dpg.texture_registry():
        texture_id = dpg.add_static_texture(width, height, data)
    img_btn = dpg.add_image_button(texture_id, width=width, height=height, tag=image_btn_tag)
    
    with dpg.popup(img_btn, tag=popup_btn_tag, no_move=True, min_size=[200, 90], max_size=[200, 90]):                 
        dpg.bind_item_theme(popup_btn_tag, create_no_padding_theme())
        dpg.add_button(label="Open in default image viewer", width=200, callback=open_image, user_data=tag_number)
        dpg.add_separator()
        dpg.add_button(label="Copy                                         ", width=200, callback=copy_image, user_data=tag_number)
        dpg.add_button(label="Delete                                       ",width=200,  callback=supprimer_image, user_data=(image_btn_tag,tag_number))
        dpg.add_separator()
        dpg.add_button(label="Read text in image                  ", width=200, callback=read_texte_in_image, user_data=tag_number)

def create_no_padding_theme():
    with dpg.theme() as theme_id:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 1)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (51, 51, 55, 255))
    return theme_id
def eceoutsdf(new=""):
    if new == 1:
        instance = ClipboardHistoryManager()

        instance.add_new_entry()
    

    do_things_with_json()
    do_things_with_image()
    

    children2 = dpg.get_item_children("img_container_but_better", 1) 
    if children2:
        for child in children2:
            dpg.delete_item(child)

    create_texture_registry()

    if texture_registry:
        for item in dpg.get_item_children(texture_registry, slot=1):
            dpg.delete_item(item)

    for img in list_images:
        tag_number = img

        with dpg.group(horizontal=True, parent="img_container_but_better"):
            add_image_with_popup(img, tag_number, width=120, height=120)


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


def registor(): 
    tag_window = f"windo_{int(time.time()*1000)}"
    with dpg.window(label="Login", tag=tag_window, width=300, height=150, pos=(250, 300/2)):
        with dpg.group(horizontal=True):
            dpg.add_text("email : ")
            email_tag = f"email_{tag_window}"
            dpg.add_input_text(width=120, tag=email_tag)
        with dpg.group(horizontal=True):
            dpg.add_text("password : ")
            password_tag = f"password_{tag_window}"
            dpg.add_input_text(width=100, tag=password_tag, password=True)

        t5 = dpg.add_button(label="Register", width=100, height=25, callback=set_credential, user_data=[email_tag, password_tag])

        dpg.add_separator()

        dpg.add_image_button(texture_tag=icon_google, width=300, height=100, callback=login_with_google)

def is_logged(): 
    
    if supabase.auth.get_user() == None:
        return False
    else:
        return True 
    
        
def get_sesion_info(): 
    sesion_info = {}
    try:
        user = supabase.auth.get_user()
        sessions_id = supabase.auth.get_session()
        sesion_info["username"] = (user.user.email).split("@")[0]
        sesion_info["access_token"] = sessions_id.access_token
        sesion_info["refresh_token"] = sessions_id.refresh_token
        return sesion_info
    except: 
        notif.show_notification(f"Error, user not logged ! ", 5, "alert")

def set_credential(sender, app_data, user_data):  
    
    email = dpg.get_value(user_data[0])
    password = dpg.get_value(user_data[1])

    try:
        supabase.auth.sign_in_with_password({"email": email, "password": password})
        notif.show_notification(f"Succesfuly logged", 3, "info")
        
        with open(".env", "w") as f:
                    f.write(f"TOKEN_ACCES={get_sesion_info()["access_token"]}\n")
                    f.write(f"REF_TOKEN={get_sesion_info()["refresh_token"]}\n")
        online_image()
    except:
        notif.show_notification(f"Wrong username/password, please try again", 3, "warning")
    


class GoogleCallback(BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code

        params = parse_qs(urlparse(self.path).query)
        code = params.get("code", [None])[0]

        if code:
            captured_code = code
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body><h2>Login successful ! You can close this tab.</h2></body></html>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<html><body><h2>No code received.</h2></body></html>")



def wait_for_google_callback(port=54321):
    server = HTTPServer(("localhost", port), GoogleCallback)
    server.handle_request() 
    server.server_close()


def login_with_google():
    global captured_code
    captured_code = None

    response = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": "http://localhost:54321",
            "scopes": "email profile"
        }
    })

    server_thread = threading.Thread(target=wait_for_google_callback, args=(54321,))
    server_thread.daemon = True
    server_thread.start()

    import webbrowser
    webbrowser.open(response.url)
    notif.show_notification("Browser opened, please log in with Google...", 4, "info")

    server_thread.join(timeout=120)

    if not captured_code:
        notif.show_notification("Google login failed or timed out", 4, "alert")
        return

    session = supabase.auth.exchange_code_for_session({"auth_code": captured_code})

    access_token = session.session.access_token
    refresh_token = session.session.refresh_token

    with open(".env", "w") as f:
        f.write(f"TOKEN_ACCES={access_token}\n")
        f.write(f"REF_TOKEN={refresh_token}\n")

    notif.show_notification("Successfully logged in with Google !", 3, "info")
    online_image()


def login_refrech(): 
    load_dotenv() 
    acces_token, recherch_token = os.getenv("TOKEN_ACCES"),os.getenv("REF_TOKEN")
    try : 
        supabase.auth.set_session(acces_token,recherch_token)
        online_image()
        notif.show_notification(f"Automaticely logged", 3, "info")
    except: 
        notif.show_notification(f"Could not login automaticely", 3, "info")

#print(get_sesion_info())


def send_to_servor() : 

    username = get_sesion_info()["username"]
    print(username)
    supabase.storage.from_('history').upload(f'{username}/history_clipboard.json', "history_clipboard.json", {'upsert': 'true',})

def get_from_servor(): 


    username = get_sesion_info()["username"]
    r = supabase.storage.from_('history').download(f'{username}/history_clipboard.json')
    if os.path.isfile("history_clipboard.json"):
        os.remove("history_clipboard.json")
        
        with open("history_clipboard.json", "wb") as f:
            f.write(r)
    else:
        with open("history_clipboard.json", "wb") as f:
            f.write(r)
    
    eceoutsdf()

def online_image(): 

    if is_logged():
        dpg.configure_item("tag_image_online_or_not", texture_tag=icon_logged)
        dpg.configure_item("text_online", color=(218, 26, 21), text="COUCOU")
        
    else:
        dpg.configure_item("tag_image_online_or_not", texture_tag=icon_not_logged)



def add_table(texte, number, json_iidddd, type): 
    if type == str("text"): 
        row_tag = f"row_{number}_{int(time.time()*1000)}"
        
        with dpg.table_row(filter_key=f"{texte}", tag=row_tag, parent=filter_table_id):
            text_tag = f"text_{number}"
            dpg.add_text(texte, tag=text_tag, wrap=400)
            dpg.add_image_button(texture_tag=copy_icon, width=40, height=40, callback=copy_texte, user_data=text_tag)
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
            dpg.add_image_button(texture_tag=copy_icon, width=40, height=40, callback=file_copy_to_cliboard, user_data=json_iidddd)
            dpg.add_image_button(texture_tag=deltet_icon, width=40, height=40, callback=supprimer_file, user_data=[row_tag, number,json_iidddd])
            dpg.add_image_button(texture_tag=open_icon, width=40, height=40, callback=open_file, user_data=[row_tag, number,json_iidddd])


with dpg.font_registry():
    default_font = dpg.add_font("OpenSans.ttf", 15)
with dpg.window(label="Magic-copy", tag="Magic-copy"):
    with dpg.menu_bar():
        with dpg.menu(label="Debug"):
            dpg.add_menu_item(label="Show About", callback=lambda:dpg.show_tool(dpg.mvTool_About))
            dpg.add_menu_item(label="Show Metrics", callback=lambda:dpg.show_tool(dpg.mvTool_Metrics))
            dpg.add_menu_item(label="Show Documentation", callback=lambda:dpg.show_tool(dpg.mvTool_Doc))
            dpg.add_menu_item(label="Show Debug", callback=lambda:dpg.show_tool(dpg.mvTool_Debug))
            dpg.add_menu_item(label="Show Style Editor", callback=lambda:dpg.show_tool(dpg.mvTool_Style))
            dpg.add_menu_item(label="Show Font Manager", callback=lambda:dpg.show_tool(dpg.mvTool_Font))
            dpg.add_menu_item(label="Show Item Registry", callback=lambda:dpg.show_tool(dpg.mvTool_ItemRegistry))
            dpg.add_menu_item(label="Show Stack Tool", callback=lambda:dpg.show_tool(dpg.mvTool_Stack))
        with dpg.menu(label="Tools"):
            dpg.add_menu_item(label="Register", callback=registor)
            
    with dpg.group(horizontal=True):
        t2 = dpg.add_button(label="coucou", width=200, height=50, arrow=True, callback=lambda:eceoutsdf(1))
        t3 = dpg.add_button(label="coucou", width=200, height=50, arrow=True, callback=send_to_servor)
        t4 = dpg.add_button(label="coucou", width=200, height=50, arrow=True, callback=get_from_servor)
        #dpg.add_separator()
        #tag_image_online_or_not = f"tag_image_online_or_not"
        dpg.add_text(label="Coucou", color="blue", tag="text_online")
        dpg.add_image(texture_tag=icon_logged, width=100, height=40, tag="tag_image_online_or_not")
        online_image()
        

    with dpg.theme() as item_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (46, 240, 146))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (48, 255, 168))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (31, 163, 99))  
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 20, 10)

        dpg.bind_item_theme(t2, item_theme)
    with dpg.theme() as item_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (168, 62, 50))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 20, 10)
        dpg.bind_item_theme(t3, item_theme)
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
            with dpg.child_window(tag="img_container_but_better",autosize_x=True, autosize_y=True,border=False, horizontal_scrollbar=True):
                    tag_number = 0
                    for img in list_images:
                        tag_number = img
                        with dpg.group(horizontal=True, parent="img_container_but_better"):
                            add_image_with_popup(img, tag_number, width=120, height=120)

                            
        with dpg.tab(label='Files '):
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
dpg.set_primary_window("Magic-copy", True)

create_texture_registry()
login_refrech()

dpg.start_dearpygui()
dpg.destroy_context()

