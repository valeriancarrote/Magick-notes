import os
import ctypes
from ctypes import windll, wintypes, byref, sizeof
import win32gui
import win32ui
from PIL import Image

import dearpygui.dearpygui as dpg

class SHFILEINFO(ctypes.Structure):
    _fields_ = [
        ("hIcon", wintypes.HANDLE),
        ("iIcon", ctypes.c_int),
        ("dwAttributes", ctypes.c_ulong),
        ("szDisplayName", ctypes.c_char * 260),
        ("szTypeName", ctypes.c_char * 80)
    ]

class IconCache:
    SHGFI_ICON = 0x000000100
    SHGFI_SMALLICON = 0x000000001
    SHGFI_LARGEICON = 0x000000000
    SHGFI_USEFILEATTRIBUTES = 0x000000010

    def __init__(self):
        self.shell32 = windll.shell32
        self._cache = {} 

    def _get_file_icon_data(self, file_path, large=False):
        shfi = SHFILEINFO()
        flags = self.SHGFI_ICON | self.SHGFI_USEFILEATTRIBUTES
        flags |= (self.SHGFI_LARGEICON if large else self.SHGFI_SMALLICON)

        res = self.shell32.SHGetFileInfoW(
            file_path,
            0,
            byref(shfi),
            sizeof(shfi),
            flags
        )
        if not res:
            return None

        hicon = shfi.hIcon
        size = 32 if large else 16
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, size, size)
        hdc_mem = hdc.CreateCompatibleDC()
        hdc_mem.SelectObject(hbmp)
        win32gui.DrawIconEx(hdc_mem.GetHandleOutput(), 0, 0, hicon, size, size, 0, None, 0x0003)

        bmp_info = hbmp.GetInfo()
        bmp_bits = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            "RGBA",
            (bmp_info["bmWidth"], bmp_info["bmHeight"]),
            bmp_bits,
            "raw", "BGRA", 0, 1
        )
        win32gui.DestroyIcon(hicon)
        hdc_mem.DeleteDC()
        hdc.DeleteDC()
        width, height = img.size
        raw_data = []
        for pixel in img.getdata():
            raw_data.extend([pixel[0] / 255, pixel[1] / 255, pixel[2] / 255, pixel[3] / 255])
        return width, height, raw_data

    def get_texture_for_file(self, file_path, large=False):

        ext = os.path.splitext(file_path)[1].lower() or ".unknown"
        if ext in self._cache:
            return self._cache[ext]

        icon_data = self._get_file_icon_data(file_path, large=large)
        if not icon_data:
            return None
        width, height, data = icon_data

        with dpg.texture_registry():
            tex_id = dpg.add_dynamic_texture(width, height, data)
        self._cache[ext] = tex_id
        return tex_id

    def clear_cache(self):
        self._cache.clear()
