

import json
import random
import os
import base64
import datetime
import shutil
from PIL import ImageGrab
import win32clipboard
import win32con
import pyperclip
from popup import NotificationManager
import ftfy

notif = NotificationManager()

HISTORY_FILE = "history_clipboard.json"

class ClipboardHistoryManager:
    def __init__(self, history_path=HISTORY_FILE, files_dir="files", images_dir="image"):
        self.history_path = history_path
        self.files_dir = files_dir
        self.images_dir = images_dir
        if not os.path.exists(self.history_path):
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump({"history": []}, f, indent=4)

    def _load_json(self):
        with open(self.history_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_json(self, data):
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def gen_id(self):
        data = self._load_json()
        existing_ids = {item["id"] for item in data["history"]}
        while True:
            candidate = random.randint(0, 999_999_999)
            if candidate not in existing_ids:
                return candidate

    def gen_date(self):
        now = datetime.datetime.now()
        
        return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}"

    def get_clipboard_files(self):
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                return list(files) if files else None
            return None
        finally:
            win32clipboard.CloseClipboard()

    def what_is_on_clipboard(self):
        """Return "Fichier", "Image", or "Texte" (or "error")."""
        files = self.get_clipboard_files()
        if files:
            return "Fichier"

        img = ImageGrab.grabclipboard()
        if img:
            return "Image"

        text = pyperclip.paste()
        if text:
            return "Texte"
        notif.show_notification("Nothing found in the clipboard", 3, "alert")
        return "error"

    def copy_clipboard_content(self):

        clip_type = self.what_is_on_clipboard()
        if clip_type == "Fichier":
            files = self.get_clipboard_files()
            path_on_clip = files[0]
            if not os.path.exists(self.files_dir):
                os.makedirs(self.files_dir)
            fixed_filename = os.path.basename(ftfy.fix_text(path_on_clip))
            dest_path = os.path.join(self.files_dir, fixed_filename)
            shutil.copy2(path_on_clip, dest_path)
            notif.show_notification(f"File copied!", 3, "info")
            return dest_path
        elif clip_type == "Image":
            img = ImageGrab.grabclipboard()
            if not os.path.exists(self.images_dir):
                os.makedirs(self.images_dir)
            img_id = self.gen_id()
            save_path = os.path.join(self.images_dir, f"{img_id}.PNG")
            img.save(save_path, "PNG")
            notif.show_notification(f"Image copyed ! ", 3, "info")
            return img_id 

        elif clip_type == "Texte":
            text = pyperclip.paste()
            
            encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            notif.show_notification(f"Text copyed ! ", 3, "info")
            return encoded

        else:
            return None

    def add_new_entry(self):
        content = self.copy_clipboard_content()
        if content is None:
            notif.show_notification(f"Nothing found in the clipboard ", 3, "alert")
            return None

        entry = {
            "content": content,
            "date": self.gen_date(),
            "type": self.what_is_on_clipboard(),
            "pinned": False,
            "id": self.gen_id()
        }
        data = self._load_json()
        data["history"].append(entry)
        self._save_json(data)
        return entry  

    def delete_entry(self, target_id):
        data = self._load_json()
        original_len = len(data["history"])
        data["history"] = [item for item in data["history"] if item["id"] != target_id]
        if len(data["history"]) < original_len:
            self._save_json(data)
            return True
        return False

    def get_all_history(self):
        return self._load_json().get("history", [])

