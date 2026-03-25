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

import ast
import sys
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any
from screeninfo import get_monitors
from file_utils import setup_mpv, find_app_path

setup_mpv()
import mpv

def get_screen_info(monitor: screeninfo.common.Monitor) -> tuple[list[int], list[int]]:
    resolution: list[int] = [int(str(monitor).split('width=')[1].split(',')[0]),
                             int(str(monitor).split('height=')[1].split(',')[0])]
    origin: list[int] = [int(str(monitor).split('x=')[1].split(',')[0]),
                         int(str(monitor).split('y=')[1].split(',')[0])]
    return resolution, origin

def initialize_gui(name: str, width: int, height: int) -> tuple[tk.Tk, dict, dict]:
    try:
        monitors_list: list = get_monitors()
    except Exception as err:
        logging.error(repr(err))
        sys.exit()
    for index, screen in enumerate(monitors_list):
        if index == 0 or ast.literal_eval(str(screen).split('is_primary=')[1].split(',')[0].replace(')', '')):
            screen_size: list[int]
            screen_position: list[int]
            screen_size, screen_position = get_screen_info(screen)

    root = tk.Tk()
    root.title(name)
    root.geometry(f'{width}x{height}+{((screen_size[0] // 2) - (width // 2)) + screen_position[0]}+{((screen_size[1] // 2) - (height // 2)) + screen_position[1]}')
    root.minsize(width=width, height=height)
    root.iconphoto(True, tk.PhotoImage(file=f'{find_app_path()[0]}/assets/icon.png'))

    font_dict: dict = {"large": "Helvetica 12 bold",
                       "small": "Helvetica 10 bold",
                       "entry": "Helvetica 10"}
    color_dict : dict = {"text_main": "#FFFFFF", #white
                         "text_dim": "#999999", #gray60
                         "bg_main": "#333333", #gray20
                         "bg_hover": "#4D4D4D", #gray30
                         "bg_widget": "#0D0D0D", #gray5
                         "bg_widget_hover": "#262626", #gray15
                         "bg_scale": "#595959", #gray35
                         "bg_button": "#404040", #gray25
                         "bg_button_hover": "#595959", #gray35
                         "border": "#101010"}

    root.config(bg=color_dict["bg_main"],
                highlightbackground=color_dict["border"],
                highlightcolor=color_dict["border"],
                highlightthickness=4)
    return root, font_dict, color_dict

def message_window(name: str, text: str, font: dict, color: dict):
    message = tk.Tk()
    message.title(name)
    message.resizable(width=False, height=False)
    message.attributes('-topmost', True)
    message.iconphoto(True, tk.PhotoImage(file=f'{find_app_path()[0]}/assets/icon.png'))
    message.config(bg=color["bg_main"],
                   highlightbackground=color["border"],
                   highlightcolor=color["border"],
                   highlightthickness=4)

    text_frame = tk.Frame(message)
    text_frame.pack(fill='both', expand=True)

    text_label = tk.Label(text_frame, text=text)
    text_label.pack(padx=16, pady=(16, 8), anchor='n')

    ok_button_frame = tk.Frame(message, bg=color["bg_main"])
    ok_button_frame.columnconfigure(0, weight=1, uniform="group1")
    ok_button_frame.columnconfigure(1, weight=1, uniform="group1")
    ok_button_frame.columnconfigure(2, weight=1, uniform="group1")

    ok_button = tk.Button(ok_button_frame,
                          text="OK",
                          command=lambda: [message.destroy(), sys.exit()])
    ok_button.grid(row=0, column=1, sticky='ews', padx=16, pady=(8, 16))

    ok_button_frame.pack(fill='x', expand=True, anchor='s', side='bottom')

    for widget0 in message.children:
        widget0 = apply_widget_theme(widget0, message, font, color)
        for widget1 in widget0.children:
            apply_widget_theme(widget1, widget0, font, color)

    message.update_idletasks()
    message.geometry(f'+{(message.winfo_screenwidth() // 2) - (message.winfo_width() // 2)}+{(message.winfo_screenheight() // 2) - (message.winfo_height() // 2)}')

    message.tk.mainloop()

def apply_widget_theme(widget: Any, parent: Any, font: dict, color: dict) -> tk.Button | tk.Checkbutton | tk.Entry | tk.Frame | tk.Label | tk.Menubutton | tk.Scale | tk.Text | ttk.Notebook:
    widget = parent.nametowidget(widget)
    match widget.winfo_class():
        case 'Button':
            widget.config(font=font["small"],
                          fg=color["text_main"],
                          bg=color["bg_button"],
                          activeforeground=color["text_main"],
                          activebackground=color["bg_button_hover"],
                          highlightbackground=color["border"])
        case 'Checkbutton':
            widget.config(font=font["small"],
                         fg=color["text_main"],
                         bg=color["bg_main"],
                         activeforeground=color["text_main"],
                         activebackground=color["bg_hover"],
                         selectcolor=color["bg_widget"],
                         highlightthickness=0)
        case 'Entry':
            widget.config(font=font["entry"],
                          fg=color["text_main"],
                          bg=color["bg_widget"],
                          insertbackground=color["text_main"],
                          highlightbackground=color["border"],
                          highlightcolor=color["text_main"],
                          highlightthickness=1)
        case 'Frame':
            widget.config(bg=color["bg_main"])
        case 'Label':
            widget.config(font=font["large"],
                          fg=color["text_main"],
                          bg=color["bg_main"])
        case 'Menubutton':
            widget.config(font=font["small"],
                          fg=color["text_main"],
                          bg=color["bg_button"],
                          activeforeground=color["text_main"],
                          activebackground=color["bg_button_hover"],
                          highlightbackground=color["border"])
            widget.children["menu"].config(font=font["small"],
                                           fg=color["text_main"],
                                           bg=color["bg_button"],
                                           activeforeground=color["text_main"],
                                           activebackground=color["bg_button_hover"])
        case 'Scale':
            widget.config(bg=color["bg_main"],
                          activebackground=color["bg_hover"],
                          troughcolor=color["bg_scale"],
                          highlightthickness=0)
        case 'Text':
            widget.config(font=font["small"],
                          fg=color["text_dim"],
                          bg=color["bg_main"],
                          insertbackground=color["text_dim"],
                          highlightthickness=0)
        case 'TNotebook':
            style = ttk.Style()
            style.theme_use('default')
            style.configure('TNotebook',
                            background=color["bg_main"],
                            borderwidth=0)
            style.configure('TNotebook.Tab',
                            font=font["small"],
                            foreground=color["text_main"],
                            background=color["bg_main"])
            style.map('TNotebook.Tab',
                      foreground=[("selected", color["text_main"])],
                      background=[("selected", color["bg_button"])])
    return widget

def exit_player(player: mpv.MPV, root: tk.Tk) -> None:
    player.quit()
    try:
        player.wait_for_shutdown(timeout=5)
    except TimeoutError:
        logging.error("Could not close pop-up, forcing window to close...")
    root.destroy()
    sys.exit()
