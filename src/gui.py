# Copyright (C) 2026 AxolHex
#
# This file is part of VisorPop.
#
# VisorPop is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# VisorPop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VisorPop.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import time
import logging
import pystray
import threading
import multiprocessing
import tkinter as tk
from PIL import Image
from typing import Any
from getpass import getuser
from platform import system
from functools import partial
from file_utils import setup_mpv, setup_logging, config_get, find_app_path, write_default_settings, read_settings_file, write_setting
from tk_utils import initialize_gui, message_window
from title_message import random_message
from reply import ReplyGUI
import visorpop

GPU_CONTEXT: str = setup_mpv()
import mpv

class MainGUI:
    def __init__(self):
        setup_logging()
        time_check: float = time.perf_counter()

        self.app_path: str
        self.settings_path: str
        self.app_path, self.settings_path = find_app_path()
        if not os.path.isfile(self.settings_path):
            write_default_settings(self.settings_path)

        settings: dict | None = read_settings_file(self.settings_path)
        if settings is None:
            self.close_window()

        #vvv DO NOT REMOVE vvv
        multiprocessing.freeze_support()

        self.root: tk.Tk
        self.font: dict
        self.color: dict
        self.root, self.font, self.color = initialize_gui(f"VisorPop — {random_message()}", 500, 500)
        self.app_image = Image.open(f'{self.app_path}/assets/icon.png')

        #Id label and entry
        self.link_id_frame = tk.Frame(self.root)
        self.link_id_frame.pack(fill='both', expand=True)

        self.link_id_label = tk.Label(self.link_id_frame, text="Link ID")
        self.link_id_label.pack(padx=16, pady=(16, 2), anchor='nw')

        self.link_id_entry = tk.Entry(self.link_id_frame)
        self.link_id_entry.pack(padx=16, pady=(2, 8), fill='x')
        self.link_id_entry.bind('<Return>', self.set_link_id)
        self.link_id_entry.bind('<KP_Enter>', self.set_link_id)
        self.link_id_enter_label = tk.Label(self.link_id_frame, text="↵")
        self.link_id_entry.bind('<KeyPress>', partial(update_entry_text, self.color["text_dim"], self.link_id_entry, self.link_id_enter_label))
        self.link_id_entry.insert(0, settings["link_id"])

        #Api key label and entry
        self.api_key_frame = tk.Frame(self.root)
        self.api_key_frame.pack(fill='both', expand=True)

        self.api_key_label = tk.Label(self.api_key_frame, text="API key")
        self.api_key_label.pack(padx=16, pady=(8, 2), anchor='nw')

        self.api_key_entry = tk.Entry(self.api_key_frame, show="*")
        self.api_key_entry.pack(padx=16, pady=(2, 8), fill='x')
        self.api_key_entry.bind('<Return>', self.set_api_key)
        self.api_key_entry.bind('<KP_Enter>', self.set_api_key)
        self.api_key_enter_label = tk.Label(self.api_key_frame,text="↵")
        self.api_key_entry.bind('<KeyPress>', partial(update_entry_text, self.color["text_dim"], self.api_key_entry, self.api_key_enter_label))
        self.api_key_entry.insert(0, settings["api_key"])

        #Download label and entry
        self.download_frame = tk.Frame(self.root)
        self.download_frame.pack(fill='both', expand=True)

        self.checkbutton_var_download = tk.BooleanVar()
        self.download_checkbutton = tk.Checkbutton(self.download_frame,
                                             text="Download",
                                             variable=self.checkbutton_var_download,
                                             command=partial(
                                                 self.set_checkbutton_var,
                                                 'download',
                                                 self.checkbutton_var_download)
                                             )
        self.download_checkbutton.pack(padx=16, pady=(8, 2), anchor='nw')
        if settings["download"]:
            self.download_checkbutton.select()

        self.save_path_entry = tk.Entry(self.download_frame)
        self.save_path_entry.pack(padx=16, pady=(2, 8), fill='x')
        self.save_path_entry.bind('<Return>', self.set_save_path)
        self.save_path_entry.bind('<KP_Enter>', self.set_save_path)
        self.save_path_enter_label = tk.Label(self.download_frame, text="↵")
        self.save_path_entry.bind('<KeyPress>', partial(update_entry_text, self.color["text_dim"], self.save_path_entry, self.save_path_enter_label))
        self.save_path_entry.insert(0, settings["save_path"])
        if settings["save_path"] == "":
            if system() == 'Windows':
                self.save_path_entry.insert(0, f'C:\\Users\\{getuser()}\\Downloads')
            else:
                self.save_path_entry.insert(0, f'/home/{getuser()}/Downloads')
            self.set_save_path()

        #Time limit label and scale
        self.time_limit_frame = tk.Frame(self.root)
        self.time_limit_frame.pack(fill='both', expand=True)

        self.time_limit_label = tk.Label(self.time_limit_frame)
        self.time_limit_label.pack(padx=(16, 4), pady=(8, 2), anchor='nw')
        if not settings["auto_close"]:
            self.time_limit_label.config(text="Pop-up time limit: None")

        self.time_limit_scale = tk.Scale(self.time_limit_frame,
                                         from_=0, to=300,
                                         resolution=5,
                                         width=16,
                                         orient='horizontal',
                                         showvalue=False,
                                         command=self.set_time_limit)
        self.time_limit_scale.pack(padx=(16, 4), pady=(2, 8), fill='x', expand=True, side='left', anchor='nw')
        self.time_limit_scale.set(settings["time_limit"])

        self.checkbutton_var_play_video = tk.BooleanVar()
        self.play_video_checkbutton = tk.Checkbutton(self.time_limit_frame,
                                               text="Finish videos",
                                               variable=self.checkbutton_var_play_video,
                                               command=partial(
                                                   self.set_checkbutton_var,
                                                   'play_video',
                                                   self.checkbutton_var_play_video)
                                               )
        self.play_video_checkbutton.pack(padx=(4, 16), pady=(2, 8), side='right', anchor='nw')
        if settings["play_video"]:
            self.play_video_checkbutton.select()

        #Pop up size label and scale
        self.popup_size_frame = tk.Frame(self.root)
        self.popup_size_frame.pack(fill='both', expand=True)

        self.popup_size_label = tk.Label(self.popup_size_frame)
        self.popup_size_label.pack(padx=(16, 4), pady=(8, 2), anchor='nw')

        self.popup_size_scale = tk.Scale(self.popup_size_frame,
                                         from_=10, to=100,
                                         width=16,
                                         orient='horizontal',
                                         showvalue=False,
                                         command=self.set_popup_size)
        self.popup_size_scale.pack(padx=(16, 4), pady=(2, 8), fill='x', expand=True, side='left', anchor='nw')
        self.popup_size_scale.set(settings["popup_size"])

        self.checkbutton_var_fullscreen = tk.BooleanVar()
        self.fullscreen_checkbutton = tk.Checkbutton(self.popup_size_frame,
                                               text="Fullscreen",
                                               variable=self.checkbutton_var_fullscreen,
                                               command=self.set_fullscreen)
        self.fullscreen_checkbutton.pack(padx=(4, 16), pady=(2, 8), side='right', anchor='nw')
        if settings["fullscreen"]:
            self.fullscreen_checkbutton.select()

        #Volume options grid
        self.options_frame = tk.Frame(self.root)
        self.options_frame.columnconfigure(0, weight=1, uniform="group1")
        self.options_frame.columnconfigure(1, weight=1, uniform="group1")

        #Notification volume label and scale
        self.notif_volume_frame = tk.Frame(self.options_frame)
        self.notif_volume_frame.grid(row=0, column=0, sticky='news')

        self.notif_volume_label = tk.Label(self.notif_volume_frame)
        self.notif_volume_label.pack(padx=(16, 4), pady=(8, 2), anchor='nw')

        self.scale_var_notif_volume = tk.IntVar()
        self.notif_volume_scale = tk.Scale(self.notif_volume_frame,
                                           from_=0, to=125,
                                           width=16,
                                           orient='horizontal',
                                           showvalue=False,
                                           variable=self.scale_var_notif_volume,
                                           command=partial(
                                               self.set_scale_var,
                                               self.notif_volume_label,
                                               "Notification volume",
                                               'notif_volume',
                                               self.scale_var_notif_volume)
                                           )
        self.notif_volume_scale.pack(padx=(16, 4), pady=(2, 8), fill='x', expand=True, anchor='nw')
        self.notif_volume_scale.set(settings["notif_volume"])

        #Video volume label and scale
        self.video_volume_frame = tk.Frame(self.options_frame)
        self.video_volume_frame.grid(row=0, column=1, sticky='news')

        self.video_volume_label = tk.Label(self.video_volume_frame)
        self.video_volume_label.pack(padx=(4, 16), pady=(8, 2), anchor='nw')

        self.scale_var_video_volume = tk.IntVar()
        self.video_volume_scale = tk.Scale(self.video_volume_frame,
                                           from_=0, to=125,
                                           width=16,
                                           orient='horizontal',
                                           showvalue=False,
                                           variable=self.scale_var_video_volume,
                                           command=partial(
                                               self.set_scale_var,
                                               self.video_volume_label,
                                               "Video volume",
                                               'video_volume',
                                               self.scale_var_video_volume)
                                           )
        self.video_volume_scale.pack(padx=(4, 16), pady=(2, 8), fill='x', expand=True, anchor='nw')
        self.video_volume_scale.set(settings["video_volume"])

        self.options_frame.pack(fill='both', expand=True)

        #Button grid
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1, uniform="group1")
        self.button_frame.columnconfigure(1, weight=1, uniform="group1")
        self.button_frame.columnconfigure(2, weight=1, uniform="group1")

        #Start, reply and quit buttons
        self.start_button = tk.Button(self.button_frame,
                                      text="Start",
                                      command=self.start_stop_popup)
        self.start_button.grid(row=0, column=0, sticky='ews', padx=(16, 4), pady=(8, 16))
        self.process_counter: int = 0
        self.active: bool = False

        self.reply_button = tk.Button(self.button_frame,
                                      text="Reply",
                                      command=self.open_reply_menu)
        self.reply_button.grid(row=0, column=1, sticky='ews', padx=4, pady=(8, 16))
        self.reply_counter: int = 0

        self.quit_button = tk.Button(self.button_frame,
                                     text="Quit",
                                     command=self.close_window)
        self.quit_button.grid(row=0, column=2, sticky='ews', padx=(4, 16), pady=(8, 16))

        self.button_frame.pack(fill='x', expand=True, anchor='sw', side='bottom')

        self.root.protocol('WM_DELETE_WINDOW', partial(self.hide_window, True))

        self.create_tray_icon()
        self.apply_menu_theme()

        logging.info(f"GUI ready in {round(time.perf_counter() - time_check, 4)} seconds")
        if settings["link_id"] == "":
            self.gpu_check()

        self.root.tk.mainloop()

    def set_link_id(self, event: tk.Event | None = None) -> bool:
        try:
            int(self.link_id_entry.get())
            write_setting(self.settings_path, 'Settings', 'link_id', self.link_id_entry.get())
            saved: bool = True
        except ValueError:
            self.reset_entry(self.link_id_entry, "is not a valid link ID", 'link_id')
            saved: bool = False
        self.link_id_enter_label.pack_forget()
        self.link_id_entry.config(fg=self.color["text_main"])
        self.link_id_entry.pack(padx=16, pady=(2, 8), fill='x')
        return saved

    def set_api_key(self, event: tk.Event | None = None) -> None:
        write_setting(self.settings_path, 'Settings', 'api_key', self.api_key_entry.get())
        self.api_key_enter_label.pack_forget()
        self.api_key_entry.config(fg=self.color["text_main"], show="*")
        self.api_key_entry.pack(padx=16, pady=(2, 8), fill='x')

    def set_save_path(self, event: tk.Event | None = None) -> bool:
        if os.path.isdir(self.save_path_entry.get()):
            write_setting(self.settings_path, 'Settings', 'save_path', self.save_path_entry.get())
            saved: bool = True
        else:
            self.reset_entry(self.save_path_entry, "is not a valid directory", 'save_path')
            saved: bool = False
        self.save_path_enter_label.pack_forget()
        self.save_path_entry.config(fg=self.color["text_main"])
        self.save_path_entry.pack(padx=16, pady=(2, 8), fill='x')
        return saved

    def set_time_limit(self, event: tk.Event) -> None:
        if self.time_limit_scale.get() == 0:
            self.time_limit_label.config(text="Pop-up time limit: None")
            auto_close: str = "False"
        else:
            self.time_limit_label.config(text=f"Pop-up time limit: {int(self.time_limit_scale.get() / 60)}:{abs((int(self.time_limit_scale.get() / 60) * 60) - self.time_limit_scale.get()):02d}")
            auto_close: str = "True"
        write_setting(self.settings_path, 'Settings', 'time_limit', self.time_limit_scale.get())
        write_setting(self.settings_path, 'Settings', 'auto_close', auto_close)

    def set_popup_size(self, event: tk.Event) -> None:
        if self.checkbutton_var_fullscreen.get():
            self.popup_size_label.config(text="Max pop-up size: Fullscreen")
        else:
            self.popup_size_label.config(text=f"Max pop-up size: {self.popup_size_scale.get()}%")
        write_setting(self.settings_path, 'Settings', 'popup_size', self.popup_size_scale.get())

    def set_fullscreen(self) -> None:
        if self.checkbutton_var_fullscreen.get():
            self.popup_size_label.config(text="Max pop-up size: Fullscreen")
        else:
            self.popup_size_label.config(text=f"Max pop-up size: {self.popup_size_scale.get()}%")
        write_setting(self.settings_path, 'Settings', 'fullscreen', self.checkbutton_var_fullscreen.get())

    def reset_entry(self, entry: tk.Entry, message: str, setting: str) -> None:
        try:
            exit_process(self.error_window)
        except AttributeError:
            pass
        logging.error(f"{entry.get()} {message}")
        self.error_window = multiprocessing.Process(target=partial(
                                                        message_window,
                                                        "VisorPop — Error",
                                                        f'"{entry.get()}" {message}.',
                                                        self.font["small"],
                                                        self.color),
                                                        name="error window",
                                                        daemon=True
                                                    )
        self.error_window.start()
        entry.delete(0, tk.END)
        entry.insert(0, config_get(self.settings_path, 'Settings', setting))

    def set_checkbutton_var(self, setting: str, var: tk.BooleanVar) -> None:
        write_setting(self.settings_path, 'Settings', setting, var.get())

    def set_scale_var(self, label: tk.Label, text: str, setting: str, var: tk.IntVar, event: tk.Event) -> None:
        label.config(text=f"{text}: {var.get()}%")
        write_setting(self.settings_path, 'Settings', setting, var.get())

    def start_stop_popup(self) -> None:
        if not self.active:
            try:
                exit_process(self.main_process)
            except AttributeError:
                pass
            if not self.set_link_id() or not self.set_save_path():
                return
            self.set_api_key()
            self.main_process = multiprocessing.Process(target=partial(visorpop.main, os.getpid()), name=f"main process {self.process_counter}")
            self.main_process.start()
            self.process_counter += 1
            logging.info(f"Started {self.main_process.name}")
            self.hide_window()
            self.start_button.config(text="Stop")
        else:
            exit_process(self.main_process)
            self.start_button.config(text="Start")
        self.active = not self.active

    def open_reply_menu(self) -> None:
        try:
            exit_process(self.reply_menu)
        except AttributeError:
            pass
        try:
            exit_process(self.error_window)
        except AttributeError:
            pass
        if not self.set_link_id():
            return
        self.set_api_key()
        if self.api_key_entry.get() == "":
            self.error_window = multiprocessing.Process(target=partial(
                                                            message_window,
                                                            "VisorPop — Error",
                                                            "An API key is required to send replies.",
                                                            self.font["small"],
                                                            self.color),
                                                            name="error window",
                                                            daemon=True
                                                        )
            self.error_window.start()
            return
        self.reply_menu = multiprocessing.Process(target=ReplyGUI, name=f"reply menu {self.reply_counter}", daemon=True)
        self.reply_menu.start()
        self.reply_counter += 1
        logging.info(f"Started {self.reply_menu.name}")

    def hide_window(self, close: bool = False) -> None:
        if pystray.Icon.HAS_MENU:
            self.root.withdraw()
            self.root.title(f"VisorPop — {random_message()}")
        elif close:
            self.close_window()

    def close_window(self, tray_icon: Any | None = None) -> None:
        try:
            exit_process(self.main_process)
        except AttributeError:
            pass
        try:
            exit_process(self.reply_menu)
        except AttributeError:
            pass
        if tray_icon is not None:
            tray_icon.stop()
        logging.info("Exiting VisorPop...\n")
        try:
            self.app_image.close()
            self.root.withdraw()
            self.root.quit()
            self.root.update()
        except AttributeError:
            sys.exit()

    def create_tray_icon(self) -> None:
        menu = (pystray.MenuItem("Open", self.root.deiconify),
                pystray.MenuItem("Reply", self.open_reply_menu),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", self.close_window))
        tray_icon = pystray.Icon("VisorPop", self.app_image, "VisorPop", menu)
        threading.Thread(target=tray_icon.run, daemon=True).start()

    def gpu_check(self) -> None:
        try:
            check = mpv.MPV(gpu_context=GPU_CONTEXT)
            check.terminate()
        except ValueError as err:
            logging.error(repr(err))
            warning_window = multiprocessing.Process(target=partial(
                                                         message_window,
                                                         "VisorPop — Warning",
                                                         "Failed to set GPU context!\nCPU will be used to process media instead.\nIt is recommended to use a Walltaker link with animations disabled to prevent high CPU usage.",
                                                         self.font["small"],
                                                         self.color),
                                                         daemon=True
                                                     )
            warning_window.start()
            warning_window.join()
            warning_window.close()

    def apply_menu_theme(self) -> None:
        self.root.config(bg=self.color["bg_main"],
                         highlightbackground=self.color["border"],
                         highlightcolor=self.color["border"],
                         highlightthickness=4)
        for frame in self.root.children:
            frame = self.root.nametowidget(frame)
            frame.config(bg=self.color["bg_main"])
            for widget in frame.children:
                widget = frame.nametowidget(widget)
                match widget.winfo_class():
                    case 'Label':
                        widget.config(font=self.font["large"],
                                      fg=self.color["text_main"],
                                      bg=self.color["bg_main"])
                    case 'Entry':
                        widget.config(font=self.font["entry"],
                                      fg=self.color["text_main"],
                                      bg=self.color["bg_widget"],
                                      insertbackground=self.color["text_main"],
                                      highlightbackground=self.color["border"],
                                      highlightcolor=self.color["text_main"],
                                      highlightthickness=1)
                    case 'Checkbutton':
                        widget.config(font=self.font["small"],
                                      fg=self.color["text_main"],
                                      bg=self.color["bg_main"],
                                      activeforeground=self.color["text_main"],
                                      activebackground=self.color["bg_hover"],
                                      selectcolor=self.color["bg_widget"],
                                      highlightthickness=0)
                    case 'Scale':
                        widget.config(bg=self.color["bg_main"],
                                      activebackground=self.color["bg_hover"],
                                      troughcolor=self.color["bg_scale"],
                                      highlightthickness=0)
                    case 'Button':
                        widget.config(font=self.font["small"],
                                      fg=self.color["text_main"],
                                      bg=self.color["bg_button"],
                                      activeforeground=self.color["text_main"],
                                      activebackground=self.color["bg_button_hover"],
                                      highlightbackground=self.color["border"])
                    case 'Frame':
                        widget.config(bg=self.color["bg_main"])
                        for item in widget.children:
                            item = widget.nametowidget(item)
                            match item.winfo_class():
                                case 'Label':
                                    item.config(font=self.font["large"],
                                                fg=self.color["text_main"],
                                                bg=self.color["bg_main"])
                                case 'Scale':
                                    item.config(bg=self.color["bg_main"],
                                                activebackground=self.color["bg_hover"],
                                                troughcolor=self.color["bg_scale"],
                                                highlightthickness=0)
        self.download_checkbutton.config(font=self.font["large"])

def update_entry_text(color: str, entry: tk.Entry, label: tk.Label, event: tk.Event) -> None:
    if event.char != "" and event.state in [0, 1, 2, 3, 16, 17, 18, 19] and not event.keysym in ['Escape', 'Tab'] or event.keysym in ['BackSpace', 'Insert', 'Delete'] or event.char in ['\x17', '\x14', '\x19', '\x04', '\x08', '\x0b', '\x18', '\x16']:
        entry.config(show="", fg=color)
        entry.pack(padx=(16, 2), pady=(2, 8), fill='x', expand=True, anchor='nw', side='left')
        label.pack(padx=(2, 16), anchor='nw', side='right')

def exit_process(process: multiprocessing.Process) -> None:
    try:
        process.terminate()
        process.join()
        process.close()
        logging.info(f"Stopped {process.name}")
    except ValueError:
        pass
    except Exception as err:
        logging.error(f"{repr(err)}\nFailed to close {process.name}")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    MainGUI()
