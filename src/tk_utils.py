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

import sys
import logging
import tkinter as tk
from file_utils import setup_mpv, find_app_path

setup_mpv()
import mpv

def initialize_gui(name: str, width: int, height: int) -> tuple[tk.Tk, dict, dict]:
    root = tk.Tk()
    root.title(name)
    root.geometry(f'{width}x{height}+{(root.winfo_screenwidth() // 2) - (width // 2)}+{(root.winfo_screenheight() // 2) - (height // 2)}')
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
    return root, font_dict, color_dict

def message_window(name: str, text: str, font: str, color: dict):
    message = tk.Tk()
    message.title(name)
    message.resizable(width=False, height=False)
    message.attributes('-topmost', True)
    message.overrideredirect(True)
    message.config(bg=color["bg_main"],
                   highlightbackground=color["border"],
                   highlightcolor=color["border"],
                   highlightthickness=4)

    text_frame = tk.Frame(message, bg=color["bg_main"])
    text_frame.pack(fill='both', expand=True)

    text_label = tk.Label(text_frame,
                          text=text,
                          font=font,
                          fg=color["text_main"],
                          bg=color["bg_main"])
    text_label.pack(padx=16, pady=(16, 8), anchor='n')

    ok_button_frame = tk.Frame(message, bg=color["bg_main"])
    ok_button_frame.columnconfigure(0, weight=1, uniform="group1")
    ok_button_frame.columnconfigure(1, weight=1, uniform="group1")
    ok_button_frame.columnconfigure(2, weight=1, uniform="group1")

    ok_button = tk.Button(ok_button_frame,
                          text="OK",
                          font=font,
                          fg=color["text_main"],
                          bg=color["bg_button"],
                          activeforeground=color["text_main"],
                          activebackground=color["bg_button_hover"],
                          highlightbackground=color["border"],
                          command=lambda: [message.destroy(), sys.exit()])
    ok_button.grid(row=0, column=1, sticky='ews', padx=16, pady=(8, 16))

    ok_button_frame.pack(fill='x', expand=True, anchor='s', side='bottom')

    message.update_idletasks()
    message.geometry(f'+{(message.winfo_screenwidth() // 2) - (message.winfo_width() // 2)}+{(message.winfo_screenheight() // 2) - (message.winfo_height() // 2)}')

    message.tk.mainloop()

def exit_player(player: mpv.MPV, root: tk.Tk) -> None:
    player.quit()
    try:
        player.wait_for_shutdown(timeout=5)
    except TimeoutError:
        logging.error("Could not close pop-up, forcing window to close...")
    root.destroy()
    sys.exit()
