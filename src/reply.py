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

import time
import logging
import requests
import tkinter as tk
from file_utils import setup_mpv, setup_logging, find_app_path, read_settings_file
from tk_utils import initialize_gui, exit_player, apply_widget_theme
from visorpop import get_json_data

GPU_CONTEXT: str = setup_mpv()
import mpv

class ReplyGUI:
    def __init__(self):
        setup_logging()
        self.settings_path: str = find_app_path()[1]

        self.root: tk.Tk
        self.font: dict
        self.color: dict
        self.root, self.font, self.color = initialize_gui("VisorPop — Reply", 500, 400)
        self.refresh_rate: float = 1 / 60

        #Header label
        self.header_label = tk.Label(self.root)
        self.header_label.pack(padx=16, pady=(16, 4), anchor='nw')

        #Reply entry
        self.reply_entry = tk.Entry(self.root)
        self.reply_entry.pack(padx=16, pady=(2, 4), fill='x')
        self.reply_entry.bind('<Return>', self.send_reply)
        self.reply_entry.bind('<KP_Enter>', self.send_reply)

        #Reply menu and buttons
        self.option_frame = tk.Frame(self.root)
        self.option_frame.columnconfigure(0, weight=1, uniform="group1")
        self.option_frame.columnconfigure(1, weight=1, uniform="group1")
        self.option_frame.columnconfigure(2, weight=1, uniform="group1")
        self.option_frame.columnconfigure(3, weight=1, uniform="group1")
        self.option_frame.columnconfigure(4, weight=1, uniform="group1")

        self.reply_type: dict = {"Love it!": "horny",
                                 "Hate it!": "disgust",
                                 "I came": "came",
                                 "Thanks": "ok"}
        self.optionmenu_var_reply = tk.StringVar(value="Love it!")
        self.reply_optionmenu = tk.OptionMenu(self.option_frame,
                                              self.optionmenu_var_reply,
                                              *self.reply_type)
        self.reply_optionmenu.grid(row=0, column=0, sticky='news', padx=(0, 4))

        self.send_button = tk.Button(self.option_frame,
                                     text="Send",
                                     command=self.send_reply)
        self.send_button.grid(row=0, column=1, sticky='news', padx=4)

        self.cancel_button = tk.Button(self.option_frame,
                                       text="Cancel",
                                       command=self.close_window)
        self.cancel_button.grid(row=0, column=4, sticky='news', padx=(4, 0))
        self.closing: bool = False

        self.option_frame.pack(padx=16, pady=(4, 8), fill='x')

        #Preview and loading label
        self.loading_label = tk.Label(self.root)

        self.preview_frame = tk.Frame(self.root)
        self.link_text = tk.Text(self.root, height=1, borderwidth=0)
        self.link_text.tag_configure("center", justify='center')

        self.root.protocol('WM_DELETE_WINDOW', self.close_window)

        self.apply_reply_theme()

        #Set up mpv preview
        self.preview = mpv.MPV(wid=str(int(self.preview_frame.winfo_id())),
                                 volume=0,
                                 loop_file='inf',
                                 hwdec='auto',
                                 profile='fast',
                                 video_sync='audio',
                                 msg_level='all=error',
                                 config=False,
                                 input_default_bindings=False,
                                 idle=True,
                                 osd_level=0,
                                 osd_bar=False,
                                 osc=False)
        try:
            self.preview.background_color = self.color["bg_main"]
        except TypeError:
            logging.error("Failed to set background color")
        try:
            self.preview.gpu_context = GPU_CONTEXT
        except TypeError:
            logging.error("Failed to set gpu context")
            self.preview.vo = GPU_CONTEXT

        timer: float = 0.0
        loading: bool = False
        current_id: str = ""
        current_count: int = -1
        while True:
            self.root.update()
            if self.closing:
                exit_player(self.preview, self.root)

            #Check if post has changed every second
            if timer < time.perf_counter():
                self.settings: dict | None = read_settings_file(self.settings_path)
                if self.settings is None:
                    self.close_window()
                    continue

                #Update link info if there's a new pop-up
                if self.settings["link_id"] != current_id or self.settings["popup_count"] != current_count and self.settings["popup_count"] is not None:
                    self.header_label.config(text="Connecting...")
                    self.preview_frame.pack_forget()
                    self.link_text.pack_forget()
                    self.loading_label.config(text="Loading preview...")
                    self.loading_label.pack(fill='both', expand=True)
                    self.root.update()
                    self.link_info: dict | None = get_json_data(f"https://walltaker.joi.how/api/links/{self.settings["link_id"]}.json", self.settings["poll_delay"])[0]
                    if self.link_info is None or self.link_info["post_url"] is None:
                        current_count = -1
                        timer = 1 + time.perf_counter()
                        continue
                    try:
                        self.set_by: str = self.link_info["set_by"]
                    except KeyError:
                        self.set_by: str = "anon"
                    current_id = self.settings["link_id"]
                    current_count = self.settings["popup_count"]

                    #Update preview
                    post_md5: str = self.link_info["post_url"].split('/')[6].split('.')[0]
                    e621_info: dict | None = get_json_data(f"https://e621.net/posts.json?md5={post_md5}", self.settings["poll_delay"])[0]
                    if e621_info is None:
                        self.loading_label.config(text="Failed to load preview")
                        self.change_header_label()
                        loading = False
                        timer = 1 + time.perf_counter()
                        continue
                    try:
                        for size in e621_info["post"]["sample"]["alternates"]["samples"]:
                            preview_url: str = e621_info["post"]["sample"]["alternates"]["samples"][size]["url"]
                            break
                    except KeyError:
                        preview_url: str = e621_info["post"]["sample"]["url"]
                    try:
                        if preview_url is None:
                            preview_url = e621_info["post"]["file"]["url"]
                    except UnboundLocalError:
                        preview_url: str = e621_info["post"]["file"]["url"]
                    self.preview.play(preview_url)
                    self.change_header_label()
                    self.root.update()
                    loading = True
                timer = 1 + time.perf_counter()

            if loading:
                try:
                    self.preview.wait_until_playing(timeout=self.refresh_rate)
                    self.loading_label.pack_forget()
                    self.preview_frame.pack(padx=16, pady=(8, 4), fill='both', expand=True)
                    self.link_text.config(state='normal')
                    self.link_text.pack(padx=16, pady=(4, 16), fill='both', anchor='s', side='bottom')
                    self.link_text.delete(1.0, tk.END)
                    self.link_text.insert(1.0, f" https://e621.net/posts/{e621_info["post"]["id"]} ")
                    self.link_text.tag_add("center", "1.0", "end")
                    self.link_text.config(state='disabled')
                    loading = False
                    continue
                except TimeoutError:
                    continue
            time.sleep(self.refresh_rate)

    def send_reply(self, event: tk.Event | None = None) -> None:
        post_data: dict = {"api_key": self.settings["api_key"],
                           "type": self.reply_type[self.optionmenu_var_reply.get()],
                           "text": self.reply_entry.get()}
        if self.optionmenu_var_reply.get() == "Hate it!":
            self.preview_frame.pack_forget()
            self.link_text.pack_forget()
            self.loading_label.config(text="Preview hidden")
            self.loading_label.pack(fill='both', expand=True)
        logging.info(f"Sending {self.reply_type[self.optionmenu_var_reply.get()]} reply to {self.set_by}: {self.reply_entry.get()}")
        self.header_label.config(text=f"Sending reply to {self.set_by}...")
        self.root.update()
        try:
            reply = requests.post(f"https://walltaker.joi.how/api/links/{self.settings["link_id"]}/response.json", headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64;)"}, json=post_data, timeout=10)
            reply.raise_for_status()
            logging.info(f"Reply sent: {self.reply_entry.get()}")
            self.header_label.config(text=f"Reply sent!")
            self.root.update()
        except Exception as err:
            logging.error(repr(err))
            self.header_label.config(text=f"Failed to send reply!")
            self.root.update()

    def change_header_label(self) -> None:
        if self.link_info["response_type"] is None:
            self.header_label.config(text=f"Reply to pop-up set by {self.set_by}:")
        else:
            self.header_label.config(text=f"Send another reply to {self.set_by}:")

    def close_window(self) -> None:
        self.closing = True

    def apply_reply_theme(self) -> None:
        self.root.config(bg=self.color["bg_main"],
                         highlightbackground=self.color["border"],
                         highlightcolor=self.color["border"],
                         highlightthickness=4)
        for widget0 in self.root.children:
            widget0 = apply_widget_theme(widget0, self.root, self.font, self.color)
            for widget1 in widget0.children:
                apply_widget_theme(widget1, widget0, self.font, self.color)
        self.loading_label.config(font=self.font["small"], fg=self.color["text_dim"])

if __name__ == "__main__":
    ReplyGUI()
