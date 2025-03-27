import pyclip
import base64
import json
import datetime
import random
from PIL import ImageGrab
import pyperclip
import PIL.Image




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
def image_or_texte():
    try:
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
        image = ImageGrab.grabclipboard()
        if image:
            print("image")
            image_id = gen_id() 
            image.save(f'image/{image_id}.PNG', 'PNG')

            return image_id
        text = pyperclip.paste()
        if text:
            cb_data = pyclip.paste() 
            #cb_data = str(cb_data)
            #print(cb_data)
            encoded_data = base64.b64encode(cb_data)
            #print(encoded_data)
            encoded_data = encoded_data.decode("utf-8")
            #print(encoded_data)
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
    #print(datee)
    acuu = "".join(datee)
    return acuu

def execution():
    y = {"content":copyer_things(),
        "date": gen_date(),
        "type": image_or_texte(),
        "pinned": "False",
        "id": gen_id()
        }
    new_copy(y)

if __name__ == "__main__":
    print("This is the main thingss")