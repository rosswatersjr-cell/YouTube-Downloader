import yt_dlp
import customtkinter as ctk
from tkinter import filedialog, Menu
import re
import os
import sys
import json
import requests
import subprocess
import pyperclip# System ClipBoard
import ctypes
from PIL import Image
from typing import Literal
from pathlib import Path

version="2026.10.07"
#Last yt-dlp version = 2026.8.19
#Last yt-dlp-ejs version = 0.8.0
class rwDialog(ctk.CTkToplevel):
    def __init__(self, parent, style: Literal["msgbox", "entry"], title, prompt, choices=None, 
                 icon: Literal["setup.png","check.png", "cancel.png", "info.png", "question.png", "warning.png"] = None, 
                 init_val=None, min_val=None, max_val=None):
        super().__init__(parent)
        self.style = style
        self.title(title)
        self.prompt = prompt
        self.choices = choices
        self.icon = icon
        self.init_val = init_val
        self.entry_var = ctk.StringVar(value=self.init_val)
        self.min_val = min_val
        self.max_val = max_val
        self.attributes("-topmost", True)
        self.grab_set()
        pgm_path=Path(__file__).parent.absolute()
        self.ico_path=os.path.join(pgm_path, 'download.ico')
        self.after(350, self.wm_iconbitmap, self.ico_path)
        self.update_idletasks()
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        self.min_window = ctypes.windll.user32.GetSystemMetrics(58)
        self.width = int(self.screen_width * 0.3)
        self.height = int(self.screen_height * 0.25)
        self.factor = (Default_DPI / 96.0)  # 96 is standard DPI for 1 point
        self.base_font_size = int(-18 * self.factor)
        self.bind("<Configure>", self.on_resize)
        self._resize_after_id = None
        self.rwDialog_font = ctk.CTkFont(family="Arial", size=self.base_font_size, weight="normal", slant="roman")
        self.result = None
        if self.icon != None:# Widget for the icon
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")                
            self.iconfile=os.path.join(base_path, self.icon)
            if self.iconfile:
                icon_size = self.height * 0.2
                pil_icon = Image.open(self.iconfile)
                ctk_image = ctk.CTkImage(light_image=pil_icon, dark_image=pil_icon, size=(icon_size, icon_size)) 
                self.icon_label = ctk.CTkLabel(self, image=ctk_image, text="")
                self.icon_label.pack(expand=True, pady=(5, 0))
        label = ctk.CTkLabel(self, text=self.prompt, font=self.rwDialog_font, anchor="w", justify="left")# Widgets for the dialog
        label.pack(pady=(10, 10))
        if self.style == "entry": 
            if self.choices is not None:
                if type(self.choices)==list:# List
                    pad_x = int(self.width * 0.15)
                    self.combobox = ctk.CTkComboBox(self, values=self.choices, font=self.rwDialog_font, button_color="#1e90ff", 
                                                    button_hover_color="#00ffff", border_width=0, command=self.on_select)   
                    self.combobox.pack(fill= "x", expand=True, padx=(pad_x, pad_x), pady=(20, 20))
                    self.combobox.focus_set() # Set focus to the entry widget
                    self.combobox.bind("<ButtonRelease-1>", self.on_mouse_release)
                    menu = self.combobox._dropdown_menu  # internal tk.Menu object
                    menu.configure(font = self.rwDialog_font)  # set dropdown font size
                    if init_val!= None: 
                        self.combobox.set(init_val)
                    self.combobox.update_idletasks()
                else:# String
                    self.entry_var.set(self.choices)
                    self.entry = ctk.CTkEntry(master=self, textvariable=self.entry_var, justify="center", font=self.rwDialog_font)
                    self.entry.pack(fill="x", expand=True, pady=(0, 0), padx=(10, 10))
                    self.entry.focus_set() # Set focus to the entry widget
                    self.entry.update_idletasks()
            else:
                self.entry = ctk.CTkEntry(self, textvariable=self.entry_var, font=self.rwDialog_font)
                self.entry.pack(pady=(0, 5), expand=True)
                self.entry.focus_set() # Set focus to the entry widget
                self.entry.update_idletasks()
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10, expand=True)
        if Language == "English": 
            txt1 = "OK"
            txt2 = "Cancel" 
        elif Language == 'Spanish': 
            txt1 = "Vale"
            txt2 = "Cancelar"
        else:# No Language Selected    
            txt1 = "OK"
            txt2 = "Cancel" 
        self.ok_button = ctk.CTkButton(self.button_frame, text=txt1, font=self.rwDialog_font, command=self.on_ok)
        self.ok_button.pack(side="left", padx=(10, 30), expand=True)
        self.cancel_button = ctk.CTkButton(self.button_frame, text=txt2, font=self.rwDialog_font, command=self.on_cancel)
        self.cancel_button.pack(side="right", padx=(30, 10), expand=True)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.update_idletasks()
        self.required_height = self.winfo_reqheight()
        self.x = int((self.screen_width / 2) - (self.width / 2))
        self.y = int((self.screen_height / 2) - (self.required_height / 2))
        self.geometry(f"{self.width}x{self.required_height}+{self.x}+{self.y}")
        parent.wait_window(self)
    def on_resize(self, event):
        if self._resize_after_id:# Debounce the Resize handler
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(100, self.handle_resize)                    
    def handle_resize(self):
        try:# Update Font Size And Icon Image    
            width = self.winfo_width()
            scale_w = width / self.width
            height = self.winfo_height()
            scale_h = height / self.required_height
            scale = min(scale_w, scale_h)  # Keep proportions
            font_size = int(self.base_font_size * scale)
            self.rwDialog_font.configure(size=font_size)
            icon_size = (self.height * 0.2) * scale
            pil_icon = Image.open(self.iconfile)
            ctk_image = ctk.CTkImage(light_image=pil_icon, dark_image=pil_icon, size=(icon_size, icon_size)) 
            self.icon_label.configure(image=ctk_image, size=(icon_size, icon_size))
        except Exception:
            return
    def on_ok(self):
        self.grab_release()
        if self.style == "entry":
            if self.choices is not None:
                if type(self.choices)==list:
                    self.result = self.combobox.get()
                else: 
                    self.result = self.entry_var.get()
            else:self.result = self.entry_var.get()
        else:self.result = None           
        self.destroy() # Close the dialog
        return self.result    
    def on_cancel(self):
        self.grab_release()
        self.result = None
        self.destroy() # Close the dialog
        return self.result    
    def on_mouse_release(self, event):
        self.update_idletasks()
    def on_select(self, choice):
        self.on_ok()                
class Youtube_URLHandler:
    def __init__(self, parent, url):
        self.parent = parent
        self.url = url
    def validate_url(self):#*
        if self.__is_youtube_video_id(self.url):
            self.url = f"https://www.youtube.com/watch?v={self.url}"
        return self.validate_url_link(self.url)
    def validate_url_link(self, url: str):# Validates the given YouTube video URL
        is_valid_link, link_type = self.__is_youtube_link(url)
        if not is_valid_link:
            return False, link_type.lower()
        return is_valid_link, link_type.lower()
    def __is_youtube_link(self, link: str):# Check if the given link is a YouTube video
        is_video = self.__is_youtube_video(link)
        is_short = self.__is_youtube_shorts(link)
        return (is_video, "Videos") if is_video \
            else (is_short, "short") if is_short \
            else (False, "unknown")
    def __is_youtube_shorts(self, link: str):# Check if the given link is a YouTube shorts link.
        shorts_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|shorts\/|watch\?.*?v=))(?:(?:[^\/\n\s]+\/)?)([a-zA-Z0-9_-]+)"
        shorts_match = re.match(shorts_pattern, link)
        return bool(shorts_match)
    def __is_youtube_video(self, link: str):# Check if the given link is a YouTube video.
        video_pattern = re.compile(
            r"^(?:https?://)?(?:www\.)?(?:youtube(?:-nocookie)?\.com/(?:(watch\?v=|watch\?feature\=share\&v=)|embed/|v/|live_stream\?channel=|live\/)|youtu\.be/)([a-zA-Z0-9_-]{11})")
        return bool(video_pattern.match(link))
    def __is_youtube_video_id(self, video_id: str):# Check if the given string is a valid YouTube video ID.
        return len(video_id) == 11 and all(
            c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in video_id)
    def not_valid_url(self, where):
        if Language == "English":
            title=f'Validate {self.parent.Download_Type.get()} URL '
            msg1=f'The {self.parent.Download_Type.get()}\n'
            msg2='URL Entered Is "Not Invalid"!\n'
            msg3='Please Entered A Valid YouTube URL!'
        else:    
            title=f'Validar {self.parent.Download_Type.get()} URL '
            msg1=f'El {self.parent.Download_Type.get()}\n'
            msg2='¡La URL Ingresada No es Inválida!\n'
            msg3='¡Por Favor, Ingresa una URL de YouTube Válida!'
        msg=msg1+msg2+msg3
        rwDialog(parent=self, style="msgbox", title=title, prompt=msg, icon="cancel.png")
        YTDLP_GUI.URL.set("")
class YTDLP_GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.num_items=0
        self.last_percentage=0.0
        self.completed_items=0
        self.URL=ctk.StringVar()
        self.geometry_str=ctk.StringVar()
        self.Download_Folder=ctk.StringVar()
        self.Download_Type=ctk.StringVar()
        self.Menu_Type=ctk.StringVar()
        self.Use_Oauth=ctk.BooleanVar()
        self.Use_Oauth.set(False)
        self.User_Name=ctk.StringVar()
        self.User_Password=ctk.StringVar()
        self.Media_Title=ctk.StringVar()
        self.Custom_Format=""
        self.Codecs_List = []
        pgm_path=Path(__file__).parent.absolute()
        self.ico_path=os.path.join(pgm_path, 'download.ico')
        self.iconbitmap(default=self.ico_path)# self.and children
        self.after(300, self.wm_iconbitmap, self.ico_path)
        self.iconbitmap(self.ico_path)
        self.attributes("-topmost", False)
        self.configure(bg="#094983")
        self.bind("<Configure>", self.on_resize)
        global Default_DPI
        global Language
        Language = ""
        data = self.read_setup()
        if len(data)==1 :# Only Theme Exist Or No DPI
            Default_DPI = self.winfo_fpixels('1i')
            data["1"] = Default_DPI
            languages=["English","Spanish"]
            title="Select Language / Seleccionar Idioma"
            msg1="Please Select The Desired Program Language.\n"
            msg2="Por favor, Seleccione el Idioma del\n"
            msg3="Programa Deseado."
            msg=msg1+msg2+msg3
            while Language == "": 
                lang = rwDialog(parent=self, style="entry", title=title, prompt=msg, choices=languages, icon="setup.png")
                if lang.result is not None:
                    Language = lang.result
                    data["2"] = Language
                    with open('Config.json', 'w') as json_file:
                        json.dump(data, json_file, indent=4)
                    json_file.close()
                else:
                    Language = ""
        else:
            Default_DPI = data["1"]    
            Language = data["2"]            
        self.user=os.getlogin()
        if Language=="English":txt="YouTube Downloader"
        else:txt="Descargador de YouTube"
        self.title(txt)
        self.resizable(True,True)
        self.protocol("WM_DELETE_WINDOW", self.youtube_destroy)
        pgm_path=Path(__file__).parent.absolute()
        self.download_path=os.path.join(os.path.expanduser("~"),"youtube_downloads.json")
        if Language == "English":file = "youtube_downloader_readme_en.txt"
        else: file = "youtube_downloader_readme_sp.txt"
        self.youtube_readme=os.path.join(pgm_path, file)
        self.ffmpeg_resources = os.path.abspath(self.resource_path("ffmpeg\\bin\\ffmpeg.exe"))
        self.deno_resources = self.resource_path("deno\\bin") 
        self.deno_path = os.path.join(self.deno_resources, "deno.exe")
        self._resize_after_id = None
        self.factor = (Default_DPI / 96.0)
        self.base_font_size = -20  # 96 is standard DPI for 1 point
        self.utube_font=ctk.CTkFont(family='Times New Romans', size=self.base_font_size, weight='normal', slant='italic')# Play List
        for r in range(9):# Configure Rows For main_frame 
            self.grid_rowconfigure(r, weight=1) 
        for c in range(12):# Configure Columns For main_frame 
            self.grid_columnconfigure(c, weight=1)
        if Language == "English":
            widget_txt = ['Open Youtube', 'Youtube Help', 'Internet Connection: ','Retry Internet Connection', 'Download Folder: ', 
                          'YouTube User Name: ', 'Use Oauth Authenication', 'YouTube Password: ', 'Download Type: ', 
                          'Enter YouTube URL: ', 'Paste', 'Download', 'Download Title: ', 'Download Progress: ']
        else:       
            widget_txt = ['Abrir YouTube', 'Ayuda de YouTube', 'Conexión a Internet: ', 'Reintentar Conexión a Internet', 
                          'Carpeta de Descargas: ', 'Nombre de Usuario de YouTube: ', 'Usar Autenticación Oauth', 'Contraseña de YouTube: ',
                          'Tipo de Descarga: ', 'Ingrese la URL de YouTube: ', 'Pegar', 'Descargar', 'Título de Descarga: ', 'Progreso de Descarga: ']
        self.open_utube = ctk.CTkButton(self, text=widget_txt[0], border_width=2, corner_radius=5, font=self.utube_font, anchor="center",
                    fg_color=("#a6e7ff", "#0c012e"), hover_color="#00ced1", text_color=("#0c012e", "#ffffff"), command=lambda:self.open_youtube())
        self.open_utube.grid(row=0, column=0, columnspan=1, rowspan=1, sticky="ew", pady=(5, 5), padx=(10, 10))
        self.utube_readme = ctk.CTkButton(self, text=widget_txt[1], border_width=2, corner_radius=5, font=self.utube_font, anchor="center",
                    fg_color=("#a6e7ff", "#0c012e"), hover_color="#00ced1", text_color=("#0c012e", "#ffffff"), command=lambda:self.open_readme())
        self.utube_readme.grid(row=0, column=1, columnspan=1, rowspan=1, sticky="ew", pady=(5, 5), padx=(0, 0))
        if Language == "English":
            menu_items = ["Menu", "Change Color Theme", "Change Language", "About YT-DLP Downloader", "Exit"]
        else:
            menu_items = ["Menú", "Cambiar Tema de Color", "Cambiar Idioma", "Acerca del Descargador YT-DLP", "Salir"]
        self.Menu_Type.set(menu_items[0])
        self.menu = ctk.CTkComboBox(self, values=menu_items, variable=self.Menu_Type, bg_color='transparent', fg_color=("#a6e7ff", "#0c012e"), 
                                           button_color="#1e90ff", button_hover_color="#00ffff", justify="left", font=self.utube_font, 
                                           border_width=0, dropdown_font=self.utube_font, corner_radius=5, command=self.menu_select) 
        self.menu.grid(row = 0, column = 2, columnspan=7, sticky = 'ew', pady=(5, 5), padx=(10, 10))
        self.conn_lbl = ctk.CTkLabel(self, text=widget_txt[2],fg_color="transparent", 
                                     font=self.utube_font, text_color=("#000000", "#ffffff"), anchor="e")
        self.conn_lbl.grid(row=1, column=0, columnspan=1, rowspan=1, sticky="ew", pady=(5, 5), padx=(0, 0))
        self.conn=self.check_internet_connection(False)
        if self.conn:# Preceed
            if Language == "English":
                text="  There is an Internet Connection  "
            else:
                text="  Hay una Conexión a Internet  "
            forecolor="#dfdfdf"
            backcolor="#369e09"
        else:# Go No Further
            if Language == "English":
                text="  No Internet Available! Check Your Connection And Try Again!  "
            else:    
                text="  ¡No hay Internet Disponible! ¡Revisa tu Conexión y Vuelve a intentarlo!  "
            forecolor="#f70505"
            backcolor="#ffffff"
        self.conn_results=ctk.CTkLabel(self, text=text, fg_color=backcolor, text_color=forecolor, 
                                       font=self.utube_font, corner_radius=10, anchor="w")
        self.conn_results.grid(row=1, column=1, columnspan=1, rowspan=1, sticky="ew", pady=(5, 5), padx=(0, 0))
        if not self.conn:
            self.retry_conn = ctk.CTkButton(self, text=widget_txt[3], border_width=2, corner_radius=5, 
                                            font=self.utube_font, anchor="center", fg_color="transparent", 
                                            hover_color="#00ced1", text_color="#dc143c")
            self.retry_conn.grid(row = 1, column = 1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
            self.retry_conn.bind("<ButtonRelease>",lambda event:self.check_internet_connection(True))
        if self.Download_Folder.get() == "":
            self.Download_Folder.set("Select Download Folder")
        self.download_lbl = ctk.CTkLabel(self, text=widget_txt[4], fg_color="transparent",
                                         text_color=("#000000", "#ffffff"), font=self.utube_font, anchor="e")
        self.download_lbl.grid(row = 2, column = 0, columnspan=1 ,sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.download_txt = ctk.CTkEntry(self, textvariable=self.Download_Folder, corner_radius=5,
                        fg_color=("#a6e7ff", "#0c012e"), text_color=("#0c012e", "#ffffff"), font=self.utube_font, state="disabled")
        self.download_txt.grid(row = 2, column = 1, columnspan=8, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.download_txt.bind("<ButtonRelease>",lambda event:self.change_download_folder(self.Download_Folder.get()))
        self.yt_user_lbl = ctk.CTkLabel(self, text=widget_txt[5],fg_color="transparent", text_color=("#000000", "#ffffff"), font=self.utube_font, anchor="e")
        self.yt_user_lbl.grid(row = 3, column = 0, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.yt_user_name = ctk.CTkEntry(self, textvariable=self.User_Name, placeholder_text="",font=self.utube_font, corner_radius=5,
                        fg_color=("#a6e7ff", "#0c012e"), text_color=("#0c012e", "#ffffff"),state="disabled")
        self.yt_user_name.grid(row = 3, column = 1, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.oauth_btn = ctk.CTkCheckBox(self, text=widget_txt[6],  border_width=2, variable=self.Use_Oauth,
                                font=self.utube_font, checkmark_color="#dfdfdf", command=lambda:self.login_status())
        self.oauth_btn.grid(row = 3, column = 2, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(15, 0))
        self.yt_pass_lbl = ctk.CTkLabel(self, text=widget_txt[7],fg_color="transparent", text_color=("#000000", "#ffffff"), anchor="e", font=self.utube_font)
        self.yt_pass_lbl.grid(row = 4, column = 0, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.yt_user_pass = ctk.CTkEntry(self, textvariable=self.User_Password, placeholder_text="", state="disabled",
                        fg_color=("#a6e7ff", "#0c012e"), text_color=("#0c012e", "#ffffff"), font=self.utube_font)
        self.yt_user_pass.grid(row = 4, column = 1, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.type_lbl = ctk.CTkLabel(self, text=widget_txt[8],fg_color="transparent", text_color=("#000000", "#ffffff"), anchor="e", font=self.utube_font)
        self.type_lbl.grid(row = 5, column = 0, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        if Language == "English":
            types=["Audio Only", "Video Only", "Video + Audio", "Custom Audio Only", "Custom Video Only", "Customize Video + Audio"]
        else:
            types=["Solo Audio", "Solo Video", "Video + Audio", "Solo Audio Personalizado", "Solo Video Personalizado", "Personalizar Video + Audio"]
        self.Download_Type.set(types[2])
        self.type_select = ctk.CTkComboBox(self, values=types, variable=self.Download_Type, bg_color='transparent', fg_color=("#a6e7ff", "#0c012e"), 
                                           button_color="#1e90ff", button_hover_color="#00ffff", justify="left", font=self.utube_font, 
                                           border_width=0, dropdown_font=self.utube_font, corner_radius=5) 
        self.type_select.grid(row = 5, column = 1, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.url_lbl = ctk.CTkLabel(self, text=widget_txt[9],fg_color="transparent", text_color=("#000000", "#ffffff"), anchor="e", font=self.utube_font)
        self.url_lbl.grid(row = 6, column = 0, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.url_txt = ctk.CTkEntry(self, textvariable=self.URL, placeholder_text="", corner_radius=5,
                        fg_color=("#a6e7ff", "#0c012e"), text_color=("#0c012e", "#ffffff"), font=self.utube_font)
        self.url_txt.grid(row = 6, column = 1, columnspan=7, sticky = 'ew', pady=(5, 5), padx=(0, 10))
        self.url_txt.bind("<KeyRelease>",lambda event:self.url_entry)
        self.url_txt.bind("<Button-3>", self.show_context_menu)
        self.context_menu = Menu(self.url_txt, tearoff=False)
        self.context_menu.add_command(label=widget_txt[10], command=lambda: self.paste_from_clipboard(self.url_txt))
        self.fetch = ctk.CTkButton(self, text=widget_txt[11], border_width=2, corner_radius=5, font=self.utube_font, anchor="center",
                    fg_color=("#a6e7ff", "#0c012e"), hover_color="#00ced1", text_color=("#0c012e", "#ffffff"))
        self.fetch.grid(row = 6, column = 8, columnspan=2, sticky = 'ew', pady=(5, 5), padx=(0, 10))
        self.fetch.bind("<ButtonRelease>",lambda event:self.download_url(self.URL.get(),self.Download_Folder.get(),self.Download_Type.get()))
        self.title_lbl = ctk.CTkLabel(self, text=widget_txt[12], fg_color="transparent", text_color="#ffffff", anchor="e", font=self.utube_font)
        self.title_lbl.grid(row = 7, column = 0, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.Media_Title.set("")
        self.URL.set("")
        self.title_name = ctk.CTkEntry(self, textvariable=self.Media_Title, placeholder_text="", corner_radius=5,
                        fg_color=("#a6e7ff", "#0c012e"), text_color=("#0c012e", "#ffffff"), font=self.utube_font)
        self.title_name.grid(row = 7, column = 1, columnspan=8, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.progress_lbl = ctk.CTkLabel(self, text=widget_txt[13],fg_color="transparent", text_color=("#000000", "#ffffff"), anchor="e", font=self.utube_font)
        self.progress_lbl.grid(row = 8, column = 0, columnspan=1, sticky = 'ew', pady=(5, 5), padx=(0, 0))
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", orientation="horizontal", corner_radius=5, bg_color="transparent")
        self.progress_bar.grid(row = 8, column = 1, columnspan=1, sticky = 'nsew', pady=(10, 10), padx=(5, 5))
        self.progress_bar.set(0)
        self.download_complete = ctk.CTkLabel(self, text='',fg_color="transparent", text_color=("#000000", "#ffffff"), anchor="w", font=self.utube_font)
        self.download_complete.grid(row = 8, column = 2 , columnspan=1, sticky = 'ew', pady=(5, 5), padx=(10, 10))
        if self.conn:
            self.open_utube.configure(state="normal")
        else:self.open_utube.configure(state="disabled")
        self.update_idletasks()
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        self.req_height = self.winfo_reqheight()
        self.req_width = self.winfo_reqwidth() + 50
        self.x=int((self.screen_width / 2) - (self.req_width / 2))
        self.y=int((self.screen_height / 2) - (self.req_height / 2))
        self.attributes("-topmost", False)
        if len(data) == 3:# Geometry Missing    
            self.geometry_str = f"{self.req_width}x{self.req_height}+{self.x}+{self.y}"
            new_data = {"3": self.geometry_str}
            with open("Config.json", "r", encoding="utf-8") as file:
                    try:
                        data = json.load(file)
                        if not isinstance(data, dict):
                            if Language == "English":
                                msg = "Error: JSON file does not contain a dictionary at the root"
                            else:
                                msg = "Error: El archivo JSON no contiene un diccionario en la raíz"     
                            raise ValueError(msg)
                    except json.JSONDecodeError:
                        data = {}
            file.close()            
            data.update(new_data)
            with open("Config.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)        
            file.close()            
        elif len(data) == 4:
            self.geometry_str = data["3"] 
        self.geometry(self.geometry_str)
        self.configure(bg="#094983")
        self.url_txt.focus_force()
        self.login_status()
        self.update()
    def on_resize(self, event):
        if self._resize_after_id:# Debounce the Resize handler
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(150, self.handle_resize)                    
    def handle_resize(self):
        try:    
            width = self.winfo_width()
            height = self.winfo_height()
            scale_w = width / self.req_width
            scale_h = height / self.req_height
            scale = min(scale_w, scale_h)  # Keep proportions
            font_size = int(self.base_font_size * scale)
            self.utube_font.configure(size=font_size)
            self.update_idletasks()
        except Exception:
            return
    def resource_path(self, relative):
        if getattr(sys, 'frozen', False):
            if hasattr(sys, "_MEIPASS"):
                return os.path.join(sys._MEIPASS, relative)
        else:
            return os.path.join(os.path.abspath("."), relative)
    def show_context_menu(self,event):
            self.context_menu.post(event.x_root, event.y_root)
    def paste_from_clipboard(self, event):
            try:
                clipboard_content=pyperclip.paste()
                if clipboard_content=="":return
                self.URL.set(clipboard_content)
            except:
                pass
    def is_playlist(self,url):
        ydl_opts = {
            'quiet': True,  # Suppress output
            'extract_flat': True}  # Extract metadata without downloading
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if info.get('_type')=='playlist':self.num_items=len(info['entries'])
                else:self.num_items=1
                self.completed_items=0
                title=info.get('title', 'Unknown Title')  # Get the title or fallback
                title=title.replace("/","_")
                self.Media_Title.set(title)
                self.update()
                return info.get('_type')=='playlist'
            except Exception as e:
                if Language == "English":
                    title="< Youtube Downloader >"
                    msg1="An Error Occured!\n"
                else:
                    title="< Descargador de YouTube >"
                    msg1="¡Ocurrió un Error!\n"
                msg2=f"{e}"
                msg=msg1+msg2
                rwDialog(parent=self, style="msgbox", title=title, prompt=msg, icon="cancel.png")
    def download_url(self, url, path, audio_video):
        self.completed_items=0
        if not self.conn:return
        if self.Use_Oauth.get():
            if self.User_Name.get()=="" or self.User_Password.get()=="":
                if Language == "English":
                    title="< YouTube Login Using Oauth Authenication >"
                    msg1="YouTube or Google Login is Required\n"
                    msg2="For Oauth Authenication! Please Enter\n"
                    msg3="a User Name and/or Password To Continue."
                else:    
                    title="< Inicio de Sesión en YouTube Usando Autenticación Oauth >"
                    msg1="¡Se RRequiere Iniciar Sesión en YouTube o Google\n"
                    msg2="para la Autenticación OAuth! Por favor Ingresa\n"
                    msg3="un Nombre de Usuario y/o Contraseña para Continuar."
                msg=msg1+msg2+msg3
                rwDialog(parent=self, style="msgbox", title=title, prompt=msg, icon="cancel.png")
                if self.User_Name.get()=="":self.yt_user_name.focus_force()
                elif self.User_Password.get()=="":self.yt_user_pass.focus_force()    
                return
        if url is None or url=="":
            if Language == "English":
                title="< YouTube Downloader URL >"
                msg1="Missing URL! Please Enter A Valid  URL!\n"
            else:    
                title="< URL del Descargador de YouTube >"
                msg1="¡URL Faltante! ¡Por favor Ingresa una URL Válida!\n"
        else:msg1 = ""    
        if self.Download_Folder.get() == "Select Download Folder" or self.Download_Folder.get() == "":
            if Language == "English":
                title="< YouTube Downloader URL >"
                msg2 = "Missing Download Folder! Please Select A Valid Folder!"
            else:
                title="< URL del Descargador de YouTube >"
                msg2 = "¡Carpeta de Descarga Faltante! ¡Por favor Selecciona una Carpeta Válida!"
        else:msg2 = ""
        if msg1 != "" or msg2 != "":
            msg = msg1 + msg2
            rwDialog(parent=self, style="msgbox", title=title, prompt=msg, icon="cancel.png")
            self.url_txt.focus_force()
            return
        self.download_complete.configure(text="")
        self.progress_bar.set(0)
        self.Media_Title.set("")
        self.update()
        if not self.is_playlist(url):
            self.num_items=1
            self.rename_video_title()
            url_handler = Youtube_URLHandler(self, url)# Instantize
            is_valid_link, link_type = url_handler.validate_url()# Only Validates And Returns link_type
            if not is_valid_link or link_type=='unknown':
                url_handler.not_valid_url('URL Link Type')
                return
            if audio_video=="Audio Only" or audio_video=="Solo Audio":# Single Audio, No Video
                self.Custom_Format = 'bestaudio[acodec^=mp4a]/bestaudio'
            elif audio_video=="Video Only" or audio_video=="Solo Video":# Single Video, No Audio
                self.Custom_Format = 'bestvideo[ext=mp4]/best'      
            elif audio_video=="Video + Audio":# Single Audio/Video
                self.Custom_Format = 'bestvideo[ext=mp4]/best+bestaudio[ext=m4a]/best'
            elif audio_video=="Custom Audio Only" or audio_video=="Solo Audio Personalizado":# Users Choice
                codecs = self.get_codecs(url)
                if Language == "English":
                    title = f"Select Format for {audio_video} Download"
                    msg1 = "Please Select The Desired Audio Format\n"
                    msg2 = "To Download From the list below:"
                else:    
                    title = f"Selecciona el Formato para Descargar {audio_video}"
                    msg1 = "Por favor, Selecciona el Formato de Audio deseas\n"
                    msg2 = "Descargar de la Lista a Continuación:"
                msg=msg1+msg2
                id = rwDialog(self, title=title, style="entry", prompt=msg, choices=codecs, init_val=None, icon=None)
                if id.result is not None:
                    comma_index = id.result.find(",", 4)  # Start searching from index 4
                    if comma_index == -1:
                        self.Custom_Format = id.result[4:]  # No comma found, return till end
                    self.Custom_Format = id.result[4:comma_index]
            elif audio_video=="Custom Video Only" or audio_video=="Solo Video Personalizado":# Users Choice
                codecs = self.get_codecs(url)
                if Language == "English":
                    title = f"Select Format for {audio_video} Download"
                    msg1 = "Please Select The Desired Video Format\n"
                    msg2 = "To Download From the list below:"
                else:    
                    title = f"Selecciona el Formato para Descargar {audio_video}"
                    msg1 = "Por favor, Selecciona el Formato de Video deseas\n"
                    msg2 = "Descargar de la Lista a Continuación:"
                msg=msg1+msg2
                id = rwDialog(self, title=title, style="entry", prompt=msg, choices=codecs, init_val=None, icon=None)
                if id.result is not None:
                    comma_index = id.result.find(",", 4)  # Start searching from index 4
                    if comma_index == -1:
                        self.Custom_Format = id.result[4:]  # No comma found, return till end
                    self.Custom_Format = id.result[4:comma_index]
            elif audio_video=="Customize Video + Audio" or audio_video=="Personalizar Video + Audio":# Users Choice
                codecs = self.get_codecs(url, av="video")
                if Language == "English":
                    title = f"Select Format for {audio_video} Download"
                    msg1 = "This Selection Merges Your Desired Video\n"
                    msg2 = "and Audio Formats. After Selecting This\n" 
                    msg3 = "Video Format, You Will Be Asked To Select\n" 
                    msg4 = "The Desired Audio Format. Please Select The\n"
                    msg5 = "Desired Video Format To Continue!"
                else:    
                    title = f"Selecciona el Formato para Descargar {audio_video}"
                    msg1 = "Esta Selección Combina los Formatos de Video y\n"
                    msg2 = "Audio que deseas. Después de Seleccionando este\n" 
                    msg3 = "Formato de Video, se te pedirá que elijas el\n" 
                    msg4 = "Formato de Audio Deseado. ¡Por favor, Selecciona\n"
                    msg5 = "el Formato de Video que deseas para Continuar!"
                msg=msg1+msg2+msg3+msg4+msg5
                id = rwDialog(self, title=title, style="entry", prompt=msg, choices=codecs, init_val=None, icon=None)
                if id.result is not None:
                    comma_index = id.result.find(",", 4)  # Start searching from index 4
                    if comma_index == -1:
                        video_id = id.result[4:]  # No comma found, return till end
                    video_id = id.result[4:comma_index]
                codecs = self.get_codecs(url, av="audio")
                if Language == "English":
                    title = f"Select Format for {audio_video} Download"
                    msg1 = "Please Select The Desired Audio Format To\n"
                    msg2 = "Merge With The Previous Selected Video Format." 
                else:    
                    title = f"Selecciona el Formato para Descargar {audio_video}"
                    msg1 = "Por favor, Selecciona el Formato de Audio que deseas\n"
                    msg2 = "Combinar con el Formato de Video Previamente Seleccionado." 
                msg=msg1+msg2
                id = rwDialog(self, title=title, style="entry", prompt=msg, choices=codecs, init_val=None, icon=None)
                if id.result is not None:
                    comma_index = id.result.find(",", 4)  # Start searching from index 4
                    if comma_index == -1:
                        audio_id = id.result[4:]  # No comma found, return till end
                    audio_id = id.result[4:comma_index]
                self.Custom_Format = f"{video_id} + {audio_id}"
            if audio_video=="Audio Only" or audio_video=="Solo Audio" or \
                audio_video=="Custom Audio Only" or audio_video=="Solo Audio Personalizado":# Users Choice:# All Audios, No Videos 
                if self.Use_Oauth.get():
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 
                                'format': self.Custom_Format, 'retries': 5, 'fragment_retries': 20, 'progress_hooks': [self.update_progressbar],
                                'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'm4a',
                                'preferredquality': '192',}],
                                'outtmpl': f'{self.Download_Folder.get()}/{self.Media_Title.get()}.%(ext)s',
                                'oauth2': True,  # Enable OAuth2 authentication
                                'username': self.User_Name.get(),  # Your account email
                                'password': self.User_Password.get()}  # Your account password
                else:    
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 
                                'format': self.Custom_Format, 'retries': 5, 'fragment_retries': 20, 'progress_hooks': [self.update_progressbar],
                                'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'm4a',
                                'preferredquality': '192',}],
                                'outtmpl': f'{self.Download_Folder.get()}/{self.Media_Title.get()}.%(ext)s'}
            elif audio_video=="Video Only" or audio_video=="Solo Video" or \
                audio_video=="Custom Video Only" or audio_video=="Solo Video Personalizado":# Single Video, No Audio
                if self.Use_Oauth.get():
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 
                                'format': self.Custom_Format, 'retries': 5, 'fragment_retries': 20, 'progress_hooks': [self.update_progressbar], 
                                'outtmpl': f'{self.Download_Folder.get()}/{self.Media_Title.get()}.%(ext)s',
                                'oauth2': True,  # Enable OAuth2 authentication
                                'username': self.User_Name.get(),  # Your account email
                                'password': self.User_Password.get()}  # Your account password
                else:    
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 'format': self.Custom_Format,
                                'retries': 5, 'fragment_retries': 20,
                                'progress_hooks': [self.update_progressbar],
                                'outtmpl': f'{self.Download_Folder.get()}/{self.Media_Title.get()}.%(ext)s'}
            elif audio_video=="Video + Audio" or audio_video=="Customize Video + Audio" or \
                audio_video=="Personalizar Video + Audio":# Single Audio/Video
                if self.Use_Oauth.get():
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 
                                'format': self.Custom_Format, 'retries': 5, 'fragment_retries': 20, 'progress_hooks': [self.update_progressbar], 
                                'outtmpl': f'{self.Download_Folder.get()}/{self.Media_Title.get()}.%(ext)s',
                                'oauth2': True,  # Enable OAuth2 authentication
                                'username': self.User_Name.get(),  # Your account email
                                'password': self.User_Password.get()}  # Your account password
                else:    
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 'format': self.Custom_Format,
                                'retries': 5, 'fragment_retries': 20,
                                'progress_hooks': [self.update_progressbar],
                                'outtmpl': f'{self.Download_Folder.get()}/{self.Media_Title.get()}.%(ext)s'}
            else:return
        else:# Play List
            if audio_video=="Audio Only" or audio_video=="Solo Audio":# All Audios, No Videos 
                if self.Use_Oauth.get():
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 'format': 'bestaudio[acodec^=mp4a]/bestaudio', 
                                'retries': 5, 'fragment_retries': 20, 'progress_hooks': [self.update_progressbar],
                                'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'm4a',
                                'preferredquality': '192',}],
                                'outtmpl': f'{self.Download_Folder.get()}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
                                'oauth2': True,  # Enable OAuth2 authentication
                                'username': self.User_Name.get(),  # Your account email
                                'password': self.User_Password.get()}  # Your account password
                else:   
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 'format': 'bestaudio[acodec^=mp4a]/bestaudio', 
                                'retries': 5, 'fragment_retries': 20, 'progress_hooks': [self.update_progressbar],
                                'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'm4a',
                                'preferredquality': '192',}],
                                'outtmpl': f'{self.Download_Folder.get()}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s'}
            elif audio_video=="Video Only" or audio_video=="Solo Video":# All Videos, No Audio
                if self.Use_Oauth.get():
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 'format': 'bestvideo[ext=mp4]/best', 'retries': 5, 
                                'fragment_retries': 20, 'progress_hooks': [self.update_progressbar], 
                                'outtmpl': f'{self.Download_Folder.get()}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
                                'oauth2': True,  # Enable OAuth2 authentication
                                'username': self.User_Name.get(),  # Your account email
                                'password': self.User_Password.get(),  # Your account password
                                'ignoreerrors': True}  # Continue downloading even if some videos fail
                else:    
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 'format': 'bestvideo[ext=mp4]/best', 'retries': 5, 'fragment_retries': 20, 
                                'progress_hooks': [self.update_progressbar],
                                'outtmpl': f'{self.Download_Folder.get()}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
                                'ignoreerrors': True}  # Continue downloading even if some videos fail
            elif audio_video=="Video + Audio" or audio_video=="Customize Video + Audio" or \
                audio_video=="Personalizar Video + Audio":# Single Audio/Video
                if self.Use_Oauth.get():
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best', 'retries': 5, 
                                'fragment_retries': 20, 'progress_hooks': [self.update_progressbar], 
                                'outtmpl': f'{self.Download_Folder.get()}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
                                'oauth2': True,  # Enable OAuth2 authentication
                                'username': self.User_Name.get(),  # Your account email
                                'password': self.User_Password.get(),  # Your account password
                                'ignoreerrors': True}  # Continue downloading even if some videos fail
                else:    
                    options = {'ffmpeg_location': self.ffmpeg_resources, 'deno': self.deno_path, 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best', 'retries': 5, 'fragment_retries': 20, 
                                'progress_hooks': [self.update_progressbar],
                                'outtmpl': f'{self.Download_Folder.get()}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
                                'ignoreerrors': True}  # Continue downloading even if some videos fail
            else:return
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
        except Exception as e:
            if Language == "English":
                title="< Youtube Downloader >"
                msg1="An Error Occurred!\n"
            else:    
                title="< Descargador de YouTube >"
                msg1="¡Ocurrió un Error!\n"
            msg2=f"{e}"
            msg=msg1+msg2
            rwDialog(parent=self, style="msgbox", title=title, prompt=msg, icon="cancel.png")
            return
        if Language == "English":
            title="< Download Status >"
            msg1="Your Download Has Completed And\n"
            msg2=f"Saved To:\n"
        else:
            title="< Estado de la Descarga >"
            msg1="Tu Descarga se ha Completado y\n"
            msg2=f"se ha Guardado en:\n"
        msg3=f"{path}"
        msg=msg1+msg2+msg3
        rwDialog(parent=self, style="msgbox", title=title, prompt=msg, icon="info.png")
        self.update()
    def get_codecs(self, url, av=None):
        codecs_list = []
        ydl_opts = {'quiet': True, 'no_warnings': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                for fmt in info.get('formats'):
                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    ext = fmt.get('ext', 'unknown')
                    fmt_id = fmt.get('format_id', 'unknown')
                    note = fmt.get('format_note', '')
                    if self.Download_Type.get() == "Custom Audio Only" or self.Download_Type.get() == "Solo Audio Personalizado" \
                        or av == "audio":
                        if vcodec == 'none' and acodec != 'none':
                            txt = f"ID: {fmt_id}, Ext: {ext}, Audio: {acodec}, Note: {note}"
                            codecs_list.append(txt)
                    elif self.Download_Type.get() == "Custom Video Only" or self.Download_Type.get() == "Solo Video Personalizado" \
                        or av == "video":
                        if vcodec != 'none' and acodec == 'none':
                            txt = f"ID: {fmt_id}, Ext: {ext}, Video: {vcodec}, Note: {note}"
                            codecs_list.append(txt)
                    else:return None        
            return codecs_list
        except Exception as e:
            return None
    def update_progressbar(self,d):
        if d['status'] == 'downloading':    
            downloaded_bytes = d.get('downloaded_bytes')
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                percentage = (downloaded_bytes / total_bytes) * 100
            else:# Fallback to the string representation if the raw number is missing/unreliable
                percentage = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            if percentage>self.last_percentage:
                if Language == "English":txt=f"Downloading: {percentage:.2f}%"
                else:txt=f"Descargando: {percentage:.2f}%"
                self.download_complete.configure(text=txt)
                self.progress_bar.set(percentage)
            self.last_percentage=percentage
        elif d['status'] == 'finished':
            self.last_percentage=0.0
            self.progress_bar.set(100)
            self.completed_items += 1
            if Language == "English":txt = "Download Complete! 100%"
            else:txt = "¡Descarga Completa! 100%"
            self.download_complete.configure(text=f"{self.completed_items} of {self.num_items} {txt}")
        elif d['status'] == 'error':
            self.last_percentage=0.0
            if Language == "English":
                title="< Download Status >"
                msg1="Error Downloading From YouTube\n"
            else:
                title="< Estado de la Descarga >"
                msg1="Error Descargando de YouTube\n"
            msg2=f"Error: {d.get('error')}"
            msg=msg1+msg2
            rwDialog(parent=self, style="msgbox", title=title, prompt=msg, icon="cancel.png")
        self.update()
    def rename_video_title(self):
            if Language == "English":
                title="< Rename Video/Audio File >"
                prompt="Rename The File Here If Desired."
            else:
                title="< Renombrar Archivo de Video/Audio >"
                prompt="Renombra el Archivo Aquí si Quieres."
            new_title = rwDialog(parent=app, style="entry", title=title, prompt=prompt, choices=self.Media_Title.get(), icon="info.png")
            if new_title.result is not None and new_title.result != '':
                self.Media_Title.set(new_title.result)
    def open_youtube(self):
        subprocess.run(['start', 'https://www.youtube.com'], shell=True)
    def open_readme(self):
        subprocess.Popen(["notepad.exe", self.youtube_readme])
    def url_entry(self):
        if self.URL.get() != "":
            self.fetch.configure(state = 'normal')
    def change_download_type(self):#*
        self.Media_Title.set("")
        self.title_name.configure(text=self.Media_Title.get())
    def change_download_folder(self,init_dir):
        if Language == "English":txt = "Please Select A Folder For YouTube Downloads"
        else:txt = "Por favor, Selecciona una Carpeta para las Descargas de YouTube"
        folder_path=filedialog.askdirectory(initialdir=init_dir, title=txt)  
        if folder_path=="" or folder_path==None:return
        self.Download_Folder.set(folder_path)
        wid=len(self.Download_Folder.get())+1 
        self.download_txt.configure(width=wid)
        self.update()
    def check_internet_connection(self,retry):
        if Language == "English":txt = "  There is an Internet Connection  "
        else:txt = "  Hay una Conexión a Internet  "
        try:
            requests.get("https://www.google.com", timeout=20)
            if retry:
                self.retry_conn.destroy()
                self.conn_results.configure(text=txt, foreground="#ffffff", background="#369e09")
                self.open_utube.configure(state="normal")
                self.update()
            return True
        except Exception:
            return False
    def login_status(self):
        if self.Use_Oauth.get()==False: 
            self.yt_user_name.configure(state="disabled")
            self.yt_user_pass.configure(state="disabled")
            self.update()
        else:    
            self.yt_user_name.configure(state="normal")
            self.yt_user_pass.configure(state="normal")
            self.yt_user_name.focus_force()
            self.update()
    def youtube_destroy(self):# X Icon Was Clicked
        try:
            self.write_setup()
            for widget in app.winfo_children():
                if isinstance(widget, ctk.CTkCanvas):widget.destroy()
                else:widget.destroy()
            os._exit(0)
        except:
            os._exit(0)
    def write_setup(self):
        self.update_idletasks()
        temp_dict={}
        sc=json.load(open("Config.json", "r"))
        json.dump(sc,open("Config.json", "w"),indent=4)
        temp_dict[0]=Theme
        temp_dict[1]=Default_DPI
        temp_dict[2]=Language
        temp_dict[3]=self.geometry()
        temp_dict[4]=self.Download_Folder.get()
        with open("Config.json", "w") as outfile:json.dump(temp_dict, outfile)
        outfile.close()
        temp_dict.clear()
    def read_setup(self):
        self.update_idletasks()
        try:
            with open('Config.json', 'r') as json_file:
                data = json.load(json_file)
                json_file.close()
            for key, value in data.items():
                global Language
                global Theme
                if key=="0":Theme = value
                elif key=="1":
                    global Default_DPI 
                    Default_DPI = value
                elif key=="2":Language = value
                elif key=="3":self.geometry_str = value
                elif key=="4":self.Download_Folder.set(value)
            return data        
        except Exception as e:
            if Language=="English":
                title='Error Reading Config.json File'
                msg1=f'Error Reading {key}, {value} In Config.json:\n'
            else:
                title='Error al Leer el Archivo Config.json\n'
                msg1=f'Error al Leer {key}, {value} en Config.json:'
            msg2= repr(e)
            msg=msg1+msg2
            rwDialog(parent=app, style="msgbox", title=title, prompt=msg, icon="cancel.png")
            pass
    def about(self):
        if Language=="English":
            title="About YT-DLP Downloader"
            msg1='Creator: Ross Waters\n'
            msg2='Email: RossWatersjr@gmail.com\n'
            msg3=f'Revision: {version}\n'
            msg4='Created For Windows 11'
        else:    
            title="Acerca del Descargador YT-DLP"
            msg1='Creador: Ross Waters\n'
            msg2='Correo Electrónico: RossWatersjr@gmail.com\n'
            msg3=f'Revisión: {version}\n'
            msg4='Creado para Windows 11'
        msg=msg1+msg2+msg3+msg4
        rwDialog(parent=self, style="msgbox", title=title, prompt=msg, icon="info.png")
        self.grab_release()
    def menu_select(self, choice):
        if choice == "Menu" or choice == "Menú":return
        elif choice == "Change Color Theme" or choice == "Cambiar Tema de Color":
            self.restart_program("theme")
        elif choice == "Change Language" or choice == "Cambiar Idioma":
            self.restart_program("language")
        elif choice == "About YT-DLP Downloader" or choice == "Acerca del Descargador YT-DLP":
            self.about()
        elif choice == "Exit" or choice == "Salir":
            self.youtube_destroy()
        self.Menu_Type.set("Menu")
    def restart_program(self, change):
        if change == "theme":
            global Theme
            if Theme == "Dark":
                Theme = "Light"
            else:    
                Theme = "Dark"
        elif change == "language":
            global Language
            if os.path.exists('Config.json'):
                if Language == "English":
                    Language = "Spanish"
                else:    
                    Language = "English"
        self.write_setup()
        try:
            for widget in self.winfo_children():# Destroys Menu Bars, Frame, Canvas And Scroll Bars
                if isinstance(widget, ctk.CTkCanvas):widget.destroy()
                else:widget.destroy()
            os.execl(sys.executable, os.path.abspath("ctkCalculator.exe"), *sys.argv) 
        except:
            pass
            os.execl(sys.executable, os.path.abspath("ctkCalculator.exe"), *sys.argv)
if __name__ == "__main__":
    root=ctk
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    ctk.DrawEngine.preferred_drawing_method = "circle_shapes"
    scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    ctk.set_widget_scaling(1.0 / scale_factor)
    ctk.set_window_scaling(1.0 / scale_factor)
    global Theme
    if os.path.exists("Config.json"):# Get Color Theme
        with open('Config.json', 'r') as json_file:
            data = json.load(json_file)
            json_file.close()
        try:        
            if data["0"]:
                Theme = data.get("0")
                ctk.set_appearance_mode(Theme)  # Options: "System", "Dark", "Light"
        except:pass        
    else:# Create json File And Set Default Theme
        data = {}                
        data["0"] = "Dark"
        Theme = "Dark"
        with open("Config.json", "w") as outfile:json.dump(data, outfile)
        outfile.close()
        ctk.set_appearance_mode("Dark")
    app = YTDLP_GUI()
    app.mainloop()

