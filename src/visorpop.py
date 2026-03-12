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
import io
import sys
import time
import random
import logging
import requests
import multiprocessing
import tkinter as tk
from PIL import Image
from psutil import pid_exists
from pymediainfo import MediaInfo
from file_utils import setup_logging, find_app_path, read_settings_file, write_setting
from popup_player import PopupPlayer

MAIN_SLEEP_TIME: int = 10

def main(parent_pid: int | None = None) -> None:
    #vvv DO NOT REMOVE vvv
    multiprocessing.freeze_support()

    setup_logging()
    popup_link: str = ""
    app_path: str
    settings_path: str
    app_path, settings_path = find_app_path()
    monitor_size: list[int] = determine_screen_size()
    loop_time: int

    while True:
        try:
            if not pid_exists(parent_pid):
                sys.exit()
        except TypeError:
            pass
        popup_link, loop_time = open_popup(popup_link, app_path, settings_path, monitor_size)
        time.sleep(loop_time)

def determine_screen_size() -> list[int]:
    root = tk.Tk()
    root.withdraw()

    width: int = root.winfo_screenwidth()
    height: int = root.winfo_screenheight()
    root.destroy()
    return [width, height]

#Checks for new pop-ups and opens them. Returns pop-up's url and sleep time
def open_popup(popup_url: str, app_folder: str, settings_file: str, screen_size: list[int]) -> tuple[str, int]:
    settings: dict | None = read_settings_file(settings_file)
    if settings is None:
        return popup_url, MAIN_SLEEP_TIME
    link_info: dict | None
    sleep_time: int
    link_info, sleep_time = get_json_data(f"https://walltaker.joi.how/api/links/{settings["link_id"]}.json")
    if link_info is None or link_info["post_url"] is None:
        return popup_url, sleep_time

    if link_info["post_url"] != popup_url:
        try:
            logging.info(f"New popup set by {link_info["set_by"]}: {link_info["post_url"]}")
        except KeyError:
            logging.info(f"New popup set by anon: {link_info["post_url"]}")
        file_name: str = link_info["post_url"].split('/')[6]
        file_type: str = link_info["post_url"].split('.')[3]

        duration: float | None
        size: list[int] | None
        input_conf: str | None
        download_data: requests.models.Response | None
        sleep_time: int
        duration, size, input_conf, download_data, sleep_time = get_media_info(app_folder, link_info["post_url"], file_type)
        if None in [duration, size, input_conf, download_data]:
            return popup_url, sleep_time

        #Change duration based on time limit
        loop_file: str = 'inf'
        if settings["auto_close"]:
            #Disable auto close if play video is enabled. Have mpv close window at end of file instead
            if settings["play_video"] and duration > settings["time_limit"]:
                settings["auto_close"] = False
                loop_file: bool = False
            else:
                duration = settings["time_limit"]

        if not settings["fullscreen"]:
            #Reduce window size if exceeding maximum size
            max_size: list[int] = [round((settings["popup_size"] / 100) * screen_size[0]),
                                   round((settings["popup_size"] / 100) * screen_size[1])]
            for i, n in zip(range(0, 2, +1), range(1, -1, -1)):
                if size[i] > max_size[i]:
                    size[n] = round((size[n] / size[i]) * max_size[i])
                    size[i] = (max_size[i])
        else:
            size = screen_size

        #Set random window position
        position: list[int] = [0, 0]
        for i in 0, 1:
            try:
                position[i] = random.randrange(0, ((screen_size[i]) - size[i]) + 1)
            except ValueError:
                pass
        logging.info(f"Duration: {duration} | Size: {size[0]}, {size[1]} | Position: {position[0]}, {position[1]}")

        file_path: str = link_info["post_url"]
        if settings["download"]:
            file_path = download_popup(settings["save_path"], file_name, download_data)
            if file_path is None:
                return popup_url, MAIN_SLEEP_TIME

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
        write_setting(settings_file, 'Settings', 'popup_count', settings["popup_count"] + 1)
        popup_url = link_info["post_url"]
    return popup_url, MAIN_SLEEP_TIME

#Returns user data
def get_json_data(json_url: str) -> tuple[dict, int] | tuple[None, int]:
    json_data: requests.models.Response | None
    wait_time: int
    json_data, wait_time = read_url(json_url, MAIN_SLEEP_TIME)
    if json_data is None:
        return None, wait_time
    return json_data.json(), MAIN_SLEEP_TIME

#Returns duration, size, mpv conf and download data
def get_media_info(path: str, url: str, extension: str) -> tuple[float, list[int], str, requests.models.Response, int] | tuple[None, None, None, None, int]:
    media: requests.models.Response | None
    wait_time: int
    media, wait_time = read_url(url, 30)
    if media is None:
        return None, None, None, None, wait_time

    if extension == "webm" or extension == "mp4":
        video = MediaInfo.parse(io.BytesIO(media.content))
        for track in video.tracks:
            if track.track_type == "Video":
                milliseconds: float = float(track.duration)
                resolution: list[int] = [int(track.width), int(track.height)]
                mpv_input: str = f'{path}/data/input_video.conf'
    else:
        with Image.open(io.BytesIO(media.content)) as image:
            milliseconds: int = 0
            while True:
                try:
                    milliseconds += image.info['duration']
                    image.seek(image.tell() + 1)
                except (EOFError, KeyError):
                    break
            resolution: list[int] = [image.size[0], image.size[1]]
            mpv_input: str = f'{path}/data/input_image.conf'
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
        response = requests.get(link, verify=True, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64;)"}, timeout=timeout_time)
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
