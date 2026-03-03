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
import re
import io
import time
import random
import logging
import requests
import multiprocessing
import tkinter as tk
from PIL import Image
from pymediainfo import MediaInfo
from setup import setup_logging, find_app_path, read_settings_file
from popup_player import PopupPlayer

MAIN_SLEEP_TIME: int = 10

def main() -> None:
    #vvv DO NOT REMOVE vvv
    multiprocessing.freeze_support()

    setup_logging()
    popup_link = ""
    app_path, settings_path = find_app_path()
    monitor_size = determine_screen_size()
    while True:
        popup_link, loop_time = open_popup(popup_link, app_path, settings_path, monitor_size)
        time.sleep(loop_time)

def determine_screen_size() -> list[int]:
    root = tk.Tk()
    root.withdraw()

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return [width, height]

#Checks for new pop-ups and opens them. Returns pop-up's url and sleep time
def open_popup(popup: str, app_folder: str, settings_file: str, screen_size: list[int]) -> tuple[str, int]:
    settings = read_settings_file(settings_file)
    if settings is None:
        return popup, MAIN_SLEEP_TIME

    url, sender, sleep_time = get_json_info(settings["link_id"])
    if None in [url, sender]:
        return popup, sleep_time

    if url != popup:
        logging.info(f"New popup set by {sender}: {url}")
        file_name, file_type = get_file_info(url)

        duration, size, input_conf, download_data, sleep_time = media_data(app_folder, url, file_type)
        if None in [duration, size, input_conf, download_data]:
            return popup, sleep_time

        #Change duration based on time limit
        loop_file = 'inf'
        if settings["auto_close"]:
            #Disable auto close if play video is enabled. Have mpv close window at end of file instead
            if settings["play_video"] and duration > settings["time_limit"]:
                settings["auto_close"] = False
                loop_file = False
            else:
                duration = settings["time_limit"]

        if not settings["fullscreen"]:
            #Reduce window size if exceeding maximum size
            max_size = [round((settings["popup_size"] / 100) * screen_size[0]),
                        round((settings["popup_size"] / 100) * screen_size[1])]
            for i, n in zip(range(0, 2, +1), range(1, -1, -1)):
                if size[i] > max_size[i]:
                    size[n] = round((size[n] / size[i]) * max_size[i])
                    size[i] = (max_size[i])
        else:
            size = screen_size

        #Set random window position
        position = [0, 0]
        for i in 0, 1:
            try:
                position[i] = random.randrange(0, ((screen_size[i]) - size[i]) + 1)
            except ValueError:
                pass
        logging.info(f"Duration: {duration} | Size: {size[0]}, {size[1]} | Position: {position[0]}, {position[1]}")

        file_path = url
        if settings["download"]:
            file_path = download_popup(settings["save_path"], file_name, download_data)
            if file_path is None:
                return popup, MAIN_SLEEP_TIME

        #Start pop-up
        multiprocessing.Process(target=PopupPlayer,
                                args=(
                                    settings["auto_close"],
                                    settings["notif_volume"],
                                    settings["video_volume"],
                                    file_name,
                                    size[0],
                                    size[1],
                                    position[0],
                                    position[1],
                                    input_conf,
                                    loop_file,
                                    file_path,
                                    app_folder,
                                    duration,
                                    os.getpid())
                                ).start()
        popup = url
    return popup, MAIN_SLEEP_TIME

#Returns url and sender
def get_json_info(link_id: str) -> tuple[str, str, int] | tuple[None, None, int]:
    json, wait_time = read_url(f"https://walltaker.joi.how/api/links/{link_id}.json", MAIN_SLEEP_TIME)
    if json is None:
        return None, None, wait_time

    file_url = re.split('"post_url":"|","post_thumbnail_url"', json.text)
    sender_name = re.split('"set_by":"|","online"|:true,"|:false,"', json.text)
    if sender_name[1] == "":
        sender_name[1] = "anon"
    return file_url[1], sender_name[1], MAIN_SLEEP_TIME

#Returns file name and file type
def get_file_info(file_url: str) -> tuple[str, str]:
    name = file_url.split('/')
    extension = file_url.split('.')
    return name[6], extension[3]

#Returns duration, size, mpv conf and download data
def media_data(path: str,file_url: str, extension: str) -> tuple[float, list[int], str, requests.models.Response, int] | tuple[None, None, None, None, int]:
    media, wait_time = read_url(file_url, 30)
    if media is None:
        return None, None, None, None, wait_time

    if extension == "webm" or extension == "mp4":
        video = MediaInfo.parse(io.BytesIO(media.content))
        for track in video.tracks:
            if track.track_type == "Video":
                milliseconds = float(track.duration)
                resolution = [int(track.width), int(track.height)]
                mpv_input = f'{path}/data/input_video.conf'
    else:
        with Image.open(io.BytesIO(media.content)) as image:
            milliseconds = 0
            while True:
                try:
                    milliseconds += image.info['duration']
                    image.seek(image.tell() + 1)
                except (EOFError, KeyError):
                    break
            resolution = [image.size[0], image.size[1]]
            mpv_input = f'{path}/data/input_image.conf'
    return milliseconds / 1000, resolution, mpv_input, media, MAIN_SLEEP_TIME

#Downloads pop-up and returns file path
def download_popup(save_path: str, save_name: str, save_data: requests.models.Response) -> str | None:
    try:
        with open(f'{save_path}/{save_name}', 'wb') as file:
            file.write(save_data.content)
    except Exception as err:
        logging.error(repr(err))
        return None
    logging.info(f"Saved: {save_path}/{save_name}")
    return f'{save_path}/{save_name}'

def read_url(link:str, timeout_time: int) -> tuple[requests.models.Response, int] | tuple[None, int]:
    try:
        response = requests.get(link, verify=True, timeout=timeout_time)
        response.raise_for_status()
    except requests.exceptions.Timeout as errt:
        logging.error(repr(errt))
        return None, 0
    except Exception as err:
        logging.error(repr(err))
        return None, MAIN_SLEEP_TIME
    return response, MAIN_SLEEP_TIME

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()
