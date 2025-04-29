import pyclip
import base64
import json
import datetime
import random
from PIL import ImageGrab
import pyperclip
import PIL.Image
import win32clipboard
import win32con
import shutil

def new_copy(new_data): 
    with open('history_clipboard.json', 'r+') as f:
        file_data = json.load(f)
        file_data["history"].append(new_data)
        f.seek(0)
        json.dump(file_data, f, indent = 4)

def gen_id(): 
    with open('history_clipboard.json', 'r') as f:
        all_id = []
        data = json.load(f) 
        num = random.randint(0,999999999)
        for item in data["history"]:
            all_id.append(item["id"])
        for same in all_id: 
            if same == num: 
                print("error ta pas de chance")
                return("error")
            if same != num: 
                return num

def get_clipboard_files():
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            return list(files) if files else None
        return None
    finally:
        win32clipboard.CloseClipboard()

def image_or_texte():
    try:
        files = get_clipboard_files()
        if files:
            return "Fichier"

        image = ImageGrab.grabclipboard()
        if image:
            return "Image"

        text = pyperclip.paste()
        if text:
            return "Texte"

        return "errror"
    except Exception as e:
        return f"Error: {e}"

def copyer_things():
    try:
        files = get_clipboard_files()
        if files:
            fifi = files[0]
            print(str(fifi))
            shutil.copy(str(fifi), r"files")
            return str(fifi)  

        image = ImageGrab.grabclipboard()
        if image:
            print("image")
            image_id = gen_id() 
            image.save(f'image/{image_id}.PNG', 'PNG')
            return image_id

        text = pyperclip.paste()
        if text:
            cb_data = pyclip.paste() 
            encoded_data = base64.b64encode(cb_data)
            encoded_data = encoded_data.decode("utf-8")
            return encoded_data

        return "errror"
    except Exception as e:
        return f"Error: {e}"

def gen_date(): 
    x = datetime.datetime.now()
    annee = x.year
    moi = x.month
    jours = x.day
    heure = x.hour
    minute = x.minute
    datee = (str(annee),"-",str(moi),"-",str(jours),"-",str(heure),"-",str(minute))
    acuu = "".join(datee)
    return acuu

def execution():
    y = {
        "content": copyer_things(),
        "date": gen_date(),
        "type": image_or_texte(),
        "pinned": "False",
        "id": gen_id()
    }
    new_copy(y)

if __name__ == "__main__":
    execution()
