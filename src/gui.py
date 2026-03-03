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
import configparser
import multiprocessing
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from typing import Any
from getpass import getuser
from platform import system
from functools import partial
from setup import setup_logging, find_app_path, write_default_settings, read_settings_file
from title_message import random_message
import visorpop

if system() == 'Windows':
    os.environ["PATH"] = f'{os.path.dirname(__file__)}/libmpv' + os.pathsep + os.environ["PATH"]
import mpv

class MainGUI:
    def __init__(self):
        setup_logging()
        time_check = time.perf_counter()

        self.config = configparser.ConfigParser()
        self.app_path, self.settings_path = find_app_path()
        if not os.path.isfile(self.settings_path):
            write_default_settings(self.settings_path)

        settings = read_settings_file(self.settings_path)
        if settings is None:
            self.close_window()
        try:
            self.config.read(self.settings_path)
        except Exception as err:
            logging.error(f"{repr(err)}\nFailed to read settings file")
            self.close_window()

        #vvv DO NOT REMOVE vvv
        multiprocessing.freeze_support()

        self.root = tk.Tk()
        self.root.geometry('500x500')
        self.app_image = Image.open(f'{self.app_path}/assets/icon.png')
        self.root.iconphoto(True, tk.PhotoImage(file=f'{self.app_path}/assets/icon.png'))

        self.font_large = "Helvetica 12 bold"
        self.font_small = "Helvetica 10 bold"
        self.font_entry = "Helvetica 10"

        #Id text and textbox
        self.link_id_frame = tk.Frame(self.root)
        self.link_id_frame.pack(fill='both', expand=True)

        self.link_id_label = tk.Label(self.link_id_frame, text="Link ID", font=self.font_large)
        self.link_id_label.pack(padx=16, pady=(16, 2), anchor='nw')

        self.link_id_entry = tk.Entry(self.link_id_frame, font=self.font_entry)
        self.link_id_entry.pack(padx=16, pady=(2, 8), fill='x')
        self.link_id_entry.bind('<Return>', self.set_link_id)
        self.link_id_entry.bind('<KP_Enter>', self.set_link_id)
        self.link_id_enter_label = tk.Label(self.link_id_frame, text="↵", font=self.font_small)
        self.link_id_entry.bind('<KeyPress>', partial(update_entry_text, self.link_id_entry, self.link_id_enter_label))
        self.link_id_entry.insert(0, settings["link_id"])

        #Download text and textbox
        self.download_frame = tk.Frame(self.root)
        self.download_frame.pack(fill='both', expand=True)

        self.checkbox_var_download = tk.BooleanVar()
        self.download_check = tk.Checkbutton(self.download_frame,
                                             text="Download",
                                             font=self.font_large,
                                             variable=self.checkbox_var_download,
                                             command=partial(self.write_setting, 'download', self.checkbox_var_download))
        self.download_check.pack(padx=16, pady=(8, 2), anchor='nw')
        if settings["download"]:
            self.download_check.select()

        self.save_path_entry = tk.Entry(self.download_frame, font=self.font_entry)
        self.save_path_entry.pack(padx=16, pady=(2, 8), fill='x')
        self.save_path_entry.bind('<Return>', self.set_save_path)
        self.save_path_entry.bind('<KP_Enter>', self.set_save_path)
        self.save_path_enter_label = tk.Label(self.download_frame, text="↵", font=self.font_small)
        self.save_path_entry.bind('<KeyPress>', partial(update_entry_text, self.save_path_entry, self.save_path_enter_label))
        self.save_path_entry.insert(0, settings["save_path"])
        if settings["save_path"] == "":
            if system() == 'Windows':
                self.save_path_entry.insert(0, f'C:\\Users\\{getuser()}\\Downloads')
            else:
                self.save_path_entry.insert(0, f'/home/{getuser()}/Downloads')
            self.set_save_path(0)

        #Time limit text and slider
        self.time_limit_frame = tk.Frame(self.root)
        self.time_limit_frame.pack(fill='both', expand=True)

        self.time_limit_label = tk.Label(self.time_limit_frame, font=self.font_large)
        self.time_limit_label.pack(padx=(16, 4), pady=(8, 2), anchor='nw')
        if not settings["auto_close"]:
            self.time_limit_label.config(text="Pop-up time limit: None")

        self.time_limit_scale = tk.Scale(self.time_limit_frame,
                                         from_=0, to=180,
                                         resolution=5,
                                         width=16,
                                         orient='horizontal',
                                         showvalue=False,
                                         command=self.set_time_limit)
        self.time_limit_scale.pack(padx=(16, 4), pady=(2, 8), fill='x', expand=True, side='left', anchor='nw')
        self.time_limit_scale.set(settings["time_limit"])

        self.checkbox_var_play_video = tk.BooleanVar()
        self.play_video_check = tk.Checkbutton(self.time_limit_frame,
                                               text="Finish videos",
                                               font=self.font_small,
                                               variable=self.checkbox_var_play_video,
                                               command=partial(self.write_setting, 'play_video', self.checkbox_var_play_video))
        self.play_video_check.pack(padx=(4, 16), pady=(2, 8), side='right', anchor='nw')
        if settings["play_video"]:
            self.play_video_check.select()

        #Pop up size text and slider
        self.popup_size_frame = tk.Frame(self.root)
        self.popup_size_frame.pack(fill='both', expand=True)

        self.popup_size_label = tk.Label(self.popup_size_frame, font=self.font_large)
        self.popup_size_label.pack(padx=(16, 4), pady=(8, 2), anchor='nw')

        self.popup_size_scale = tk.Scale(self.popup_size_frame,
                                         from_=10, to=100,
                                         width=16,
                                         orient='horizontal',
                                         showvalue=False,
                                         command=self.set_popup_size)
        self.popup_size_scale.pack(padx=(16, 4), pady=(2, 8), fill='x', expand=True, side='left', anchor='nw')
        self.popup_size_scale.set(settings["popup_size"])

        self.checkbox_var_fullscreen = tk.BooleanVar()
        self.fullscreen_check = tk.Checkbutton(self.popup_size_frame,
                                               text="Fullscreen",
                                               font=self.font_small,
                                               variable=self.checkbox_var_fullscreen,
                                               command=self.set_fullscreen)
        self.fullscreen_check.pack(padx=(4, 16), pady=(2, 8), side='right', anchor='nw')
        if settings["fullscreen"]:
            self.fullscreen_check.select()

        #Volume options grid
        self.options_frame = tk.Frame(self.root)
        self.options_frame.columnconfigure(0, weight=1, uniform="group1")
        self.options_frame.columnconfigure(1, weight=1, uniform="group1")

        #Notification volume text and slider
        self.notif_volume_frame = tk.Frame(self.options_frame)
        self.notif_volume_frame.grid(row=0, column=0, sticky='news')

        self.notif_volume_label = tk.Label(self.notif_volume_frame, font=self.font_large)
        self.notif_volume_label.pack(padx=(16, 4), pady=(8, 2), anchor='nw')

        self.scale_var_notif_volume = tk.IntVar()
        self.notif_volume_scale = tk.Scale(self.notif_volume_frame,
                                           from_=0, to=125,
                                           width=16,
                                           orient='horizontal',
                                           showvalue=False,
                                           variable=self.scale_var_notif_volume,
                                           command=partial(self.set_scale_var, self.notif_volume_label, "Notification volume", 'notif_volume', self.scale_var_notif_volume))
        self.notif_volume_scale.pack(padx=(16, 4), pady=(2, 8), fill='x', expand=True, anchor='nw')
        self.notif_volume_scale.set(settings["notif_volume"])

        #Video volume text and slider
        self.video_volume_frame = tk.Frame(self.options_frame)
        self.video_volume_frame.grid(row=0, column=1, sticky='news')

        self.video_volume_label = tk.Label(self.video_volume_frame, font=self.font_large)
        self.video_volume_label.pack(padx=(4, 16), pady=(8, 2), anchor='nw')

        self.scale_var_video_volume = tk.IntVar()
        self.video_volume_scale = tk.Scale(self.video_volume_frame,
                                           from_=0, to=125,
                                           width=16,
                                           orient='horizontal',
                                           showvalue=False,
                                           variable=self.scale_var_video_volume,
                                           command=partial(self.set_scale_var, self.video_volume_label, "Video volume", 'video_volume', self.scale_var_video_volume))
        self.video_volume_scale.pack(padx=(4, 16), pady=(2, 8), fill='x', expand=True, anchor='nw')
        self.video_volume_scale.set(settings["video_volume"])

        self.options_frame.pack(fill='both', expand=True)

        #Button grid
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.columnconfigure(0, weight=1, uniform="group1")
        self.buttons_frame.columnconfigure(1, weight=1, uniform="group1")

        #Start and quit buttons
        self.start_button = tk.Button(self.buttons_frame,
                                      text="Start",
                                      font=self.font_small,
                                      command=self.start_stop_popup)
        self.start_button.grid(row=0, column=0, sticky='ews', padx=(16, 4), pady=(8, 16))
        self.process_counter = 0
        self.active = False

        self.quit_button = tk.Button(self.buttons_frame,
                                     text="Quit",
                                     font=self.font_small,
                                     command=self.close_window)
        self.quit_button.grid(row=0, column=1, sticky='ews', padx=(4, 16), pady=(8, 16))

        self.buttons_frame.pack(fill='x', expand=True, anchor='sw', side='bottom')

        self.root.protocol('WM_DELETE_WINDOW', partial(self.hide_window, True))
        self.create_tray_icon()

        logging.info(f"GUI ready in {round(time.perf_counter() - time_check, 4)} seconds")
        self.show_window()
        if settings["link_id"] == "":
            gpu_check()

        self.root.tk.mainloop()

    def set_link_id(self, event: tk.Event | int) -> bool:
        try:
            int(self.link_id_entry.get())
            self.write_setting('link_id', self.link_id_entry)
            saved = True
        except ValueError:
            logging.error(f"{self.link_id_entry.get()} is not a valid link ID")
            messagebox.showerror("VisorPop — Error", f'"{self.link_id_entry.get()}" is not a valid link ID.')
            self.link_id_entry.delete(0, tk.END)
            self.link_id_entry.insert(0, self.config.get('Settings', 'link_id'))
            saved = False
        self.link_id_enter_label.pack_forget()
        self.link_id_entry.config(fg='black')
        self.link_id_entry.pack(padx=16, pady=(2, 8), fill='x')
        return saved

    def set_save_path(self, event: tk.Event | int) -> bool:
        if os.path.isdir(self.save_path_entry.get()):
            self.write_setting('save_path', self.save_path_entry)
            saved = True
        else:
            logging.error(f"{self.save_path_entry.get()} is not a valid directory")
            messagebox.showerror("VisorPop — Error", f'"{self.save_path_entry.get()}" is not a valid directory.')
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, self.config.get('Settings', 'save_path'))
            saved = False
        self.save_path_enter_label.pack_forget()
        self.save_path_entry.config(fg='black')
        self.save_path_entry.pack(padx=16, pady=(2, 8), fill='x')
        return saved

    def set_time_limit(self, event: tk.Event) -> None:
        if self.time_limit_scale.get() == 0:
            self.time_limit_label.config(text="Pop-up time limit: None")
            self.config.set('Settings', 'auto_close', str(False))
        else:
            self.time_limit_label.config(text=f"Pop-up time limit: {int(self.time_limit_scale.get() / 60)}:{abs((int(self.time_limit_scale.get() / 60) * 60) - self.time_limit_scale.get()):02d}")
            self.config.set('Settings', 'auto_close', str(True))
        self.write_setting('time_limit', self.time_limit_scale)

    def set_popup_size(self, event: tk.Event) -> None:
        if self.checkbox_var_fullscreen.get():
            self.popup_size_label.config(text="Max pop-up size: Fullscreen")
        else:
            self.popup_size_label.config(text=f"Max pop-up size: {self.popup_size_scale.get()}%")
        self.write_setting('popup_size', self.popup_size_scale)

    def set_fullscreen(self) -> None:
        if self.checkbox_var_fullscreen.get():
            self.popup_size_label.config(text="Max pop-up size: Fullscreen")
        else:
            self.popup_size_label.config(text=f"Max pop-up size: {self.popup_size_scale.get()}%")
        self.write_setting('fullscreen', self.checkbox_var_fullscreen)

    def set_scale_var(self, label: tk.Label, text: str, setting: str, var: tk.IntVar, event: tk.Event) -> None:
        label.config(text=f"{text}: {var.get()}%")
        self.write_setting(setting, var)

    def write_setting(self, setting: str, var: tk.Entry | tk.BooleanVar | tk.Scale | tk.IntVar) -> None:
        self.config.set('Settings', setting, str(var.get()))
        try:
            with open(self.settings_path, 'w') as file:
                self.config.write(file)
            logging.debug(f"{setting} set to {var.get()}")
        except Exception as err:
            logging.error(f"{repr(err)}\nFailed to save {setting} as {var.get()}")

    def start_stop_popup(self) -> None:
        if not self.active:
            link_id_check = self.set_link_id(0)
            save_path_check = self.set_save_path(0)
            if not link_id_check or not save_path_check:
                return
            self.get_popups = multiprocessing.Process(target=visorpop.main, name=f"main process {self.process_counter}")
            self.get_popups.start()
            self.process_counter += 1
            logging.info(f"Started {self.get_popups.name}")
            self.hide_window()
            self.start_button.config(text="Stop")
        else:
            exit_process(self.get_popups)
            self.start_button.config(text="Start")
        self.active = not self.active

    def hide_window(self, close: bool = False) -> None:
        if pystray.Icon.HAS_MENU:
            self.root.withdraw()
        elif close:
            self.close_window()

    def show_window(self) -> None:
        self.root.title(f"VisorPop — {random_message()}")
        self.root.deiconify()

    def close_window(self, tray_icon: Any | None = None) -> None:
        try:
            exit_process(self.get_popups)
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
        menu = (pystray.MenuItem("Open", self.show_window),
                pystray.MenuItem("Quit", self.close_window))
        tray_icon = pystray.Icon("VisorPop", self.app_image, "VisorPop", menu)
        threading.Thread(target=tray_icon.run, daemon=True).start()

def gpu_check() -> None:
    if system() == 'Linux':
        try:
            check = mpv.MPV(gpu_context='x11')
            check.terminate()
        except ValueError as err:
            logging.error(repr(err))
            messagebox.showwarning("VisorPop — Warning", "Failed to set GPU context!\nCPU will be used to process media instead.\nIt is recommended to use a Walltaker link with animations disabled to prevent high CPU usage.")

def update_entry_text(entry: tk.Entry, label: tk.Label, event: tk.Event) -> None:
    if event.char != "" and event.state in [0, 1, 2, 3, 16, 17, 18, 19] and not event.keysym in ['Escape', 'Tab'] or event.keysym in ['BackSpace', 'Insert', 'Delete'] or event.char in ['\x17', '\x14', '\x19', '\x04', '\x08', '\x0b', '\x18', '\x16']:
        entry.config(fg='dimgray')
        entry.pack(padx=(16, 4), pady=(2, 8), fill='x', expand=True, anchor='nw', side='left')
        label.pack(padx=(4, 16), anchor='nw', side='right')

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
