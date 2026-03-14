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
import time
import logging
import threading
import tkinter as tk
from psutil import pid_exists
from functools import partial
from file_utils import setup_mpv, setup_logging
from tk_utils import exit_player

GPU_CONTEXT: str = setup_mpv()
import mpv

class PopupPlayer(tk.Tk):
    def __init__(self,
                 auto_close: bool,
                 notif_volume: int,
                 video_volume: int,
                 image_name: str,
                 size_x: int,
                 size_y: int,
                 position_x: int,
                 position_y: int,
                 input_file: str,
                 loop: str | bool,
                 media_file: str,
                 program_folder: str,
                 popup_duration: float,
                 parent_pid: int):
        super().__init__()
        setup_logging()
        self.withdraw()
        #Keep this self.update(). Pop-up windows sometimes fail to start without it
        self.update()
        self.title(image_name)
        self.geometry(f'{size_x}x{size_y}+{position_x}+{position_y}')
        self.resizable(width=False, height=False)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.refresh_rate: float = 1 / 30

        #Pop-up controls for Windows system. Linux uses input-image.conf or input-video.conf
        self.bind('<Double-Button-1>', self.pause_player)
        self.bind('<Button-3>', self.disable_time_limit)
        self.protocol('WM_DELETE_WINDOW', self.pause_player)
        if input_file == f'{program_folder}/data/input_video.conf':
            self.bind('<MouseWheel>', self.change_video_volume)

        #Setup mpv in tk window
        self.player = mpv.MPV(wid=str(int(self.winfo_id())),
                              volume=video_volume,
                              input_conf=input_file,
                              loop_file=loop,
                              hwdec='auto',
                              profile='fast',
                              video_sync='display-resample',
                              msg_level='all=error',
                              config=False,
                              input_default_bindings=False,
                              idle=True,
                              volume_max=125,
                              osd_level=1,
                              osd_duration=3000,
                              osd_bar=False,
                              osd_align_x='center',
                              osd_align_y='bottom',
                              osd_font='Helvetica',
                              osd_font_size=48,
                              osc=False)
        try:
            self.player.gpu_context = GPU_CONTEXT
        except TypeError:
            logging.error("Failed to set gpu context")
            self.player.vo = GPU_CONTEXT
        self.player.play(media_file)

        #Wait until playback starts to show window and play notification sound
        logging.info(f"Loading: {image_name}")
        playing: bool = False
        counter: int = 0
        while not playing:
            try:
                self.player.wait_until_playing(timeout=10)
                playing = True
            except TimeoutError:
                if not pid_exists(parent_pid) or counter >= 30:
                    logging.error(f"Failed to open: {image_name}")
                    self.close_popup(f"Exiting: {image_name}")
                self.player.stop()
                self.player.play(media_file)
            counter += 1
        threading.Thread(target=partial(play_notif_sound, notif_volume, program_folder), daemon=True).start()
        logging.info(f"Opened: {image_name}")
        self.deiconify()

        timer: float = popup_duration + time.perf_counter()
        while True:
            self.update()
            #Close when time expires, if mpv is paused, if mpv core fails or if parent process is closed
            if auto_close and timer <= time.perf_counter() or self.player.pause or self.player.core_shutdown is not False or not pid_exists(parent_pid):
                self.close_popup(f"Closing: {image_name}")
            #Disables time limit if player osd level changes
            if not self.player.osd_level:
                self.player.osd_level = 1
                if auto_close or not self.player.loop_file:
                    auto_close = False
                    self.player.loop_file = 'inf'
                    self.player.command('show-text', "Time limit: None")
            try:
                self.player.wait_for_event('end_file', timeout=self.refresh_rate)
                self.close_popup(f"Closing: {image_name}")
            except TimeoutError:
                pass

    def pause_player(self, event: tk.Event | None = None) -> None:
        self.player.pause = True

    def disable_time_limit(self, event: tk.Event) -> None:
        self.player.osd_level = 0

    def change_video_volume(self, event: tk.Event) -> None:
        if event.delta > 0:
            self.player.volume += 5
        else:
            self.player.volume -= 5
        if self.player.volume > 125:
            self.player.volume = 125
        elif self.player.volume < 0:
            self.player.volume = 0
        self.player.command('show-text', f"Volume: {round(self.player.volume)}%")

    def close_popup(self, message: str) -> None:
        logging.info(message)
        self.player.quit()
        exit_player(self.player, self)

def play_notif_sound(notif_volume: int, path: str) -> None:
    audio = mpv.MPV(volume=notif_volume,
                    hwdec='auto',
                    profile='fast',
                    msg_level='all=error',
                    config=False,
                    input_default_bindings=False,
                    force_window=False,
                    loop_file=0)
    audio.play(f'{path}/assets/AeroCE_TriTone_up.wav')
    try:
        audio.wait_for_playback(timeout=5)
    except TimeoutError:
        logging.error("Failed to play notification audio")
    audio.quit()
    sys.exit()

if __name__ == "__main__":
    sys.exit()
