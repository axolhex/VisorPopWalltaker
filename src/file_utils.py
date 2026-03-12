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
import logging
import configparser
from typing import Any
from platform import system
from datetime import datetime

config = configparser.ConfigParser()

def setup_mpv() -> str:
    if system() == 'Windows':
        os.environ["PATH"] = f'{os.path.dirname(__file__)}/libmpv' + os.pathsep + os.environ["PATH"]
    display: str = ''
    if system() == 'Linux':
        display = 'x11'
    return display

def setup_logging() -> None:
    if not os.path.isdir(f'{find_app_path()[0]}/logs'):
        os.mkdir(f'{find_app_path()[0]}/logs')
    logging.basicConfig(level=logging.INFO,
                        filename=f'{find_app_path()[0]}/logs/{datetime.today().strftime("%d-%m-%Y")}.log',
                        format='%(asctime)s [%(levelname)s] — %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S')

def config_read(file_path: str) -> bool:
    try:
        config.read(file_path)
        return True
    except Exception as err:
        logging.error(f"{repr(err)}\nFailed to read: {file_path}")
        return False

def config_get(config_path: str, section: str, option: str) -> str | None:
    if not config_read(config_path):
        return None
    try:
        var = config.get(section, option)
    except Exception as err:
        logging.error(repr(err))
        return None
    return var

#Determines if running as script or executable and returns app's and settings file's path
def find_app_path() -> tuple[str, str]:
    if getattr(sys, 'frozen', False):
        os.environ["REQUESTS_CA_BUNDLE"] = f'{os.path.dirname(__file__)}/certifi/cacert.pem'
        app: str = str(os.path.dirname(__file__))
        settings: str = f'{os.path.dirname(sys.executable)}/settings.ini'
    else:
        app: str = str(os.path.split(os.path.dirname(__file__))[0])
        settings: str = f'{os.path.split(os.path.dirname(__file__))[0]}/settings.ini'
    return app, settings

def write_default_settings(settings_ini: str) -> None:
    config.add_section('Settings')
    config.set('Settings', 'link_id', "")
    config.set('Settings', 'api_key', "")
    config.set('Settings', 'download', "False")
    config.set('Settings', 'save_path', "")
    config.set('Settings', 'time_limit', "60")
    config.set('Settings', 'auto_close', "True")
    config.set('Settings', 'play_video', "True")
    config.set('Settings', 'popup_size', "50")
    config.set('Settings', 'fullscreen', "False")
    config.set('Settings', 'notif_volume', "75")
    config.set('Settings', 'video_volume', "50")
    config.set('Settings', 'popup_count', "0")
    try:
        with open(settings_ini, 'w') as file:
            config.write(file)
        logging.info(f"Created settings file: {settings_ini}")
    except Exception as err:
        logging.error(f"{repr(err)}\nFailed to write default settings")
        sys.exit()

#Returns all settings as dictionary
def read_settings_file(settings_ini: str) -> dict | None:
    if not config_read(settings_ini):
        return None
    try:
        link_id: str = config.get('Settings', 'link_id')
        api_key: str = config.get('Settings', 'api_key')
        download: bool = config.getboolean('Settings', 'download')
        save_path: str = config.get('Settings', 'save_path')
        time_limit: int = config.getint('Settings', 'time_limit')
        auto_close: bool = config.getboolean('Settings', 'auto_close')
        play_video: bool = config.getboolean('Settings', 'play_video')
        popup_size: int = config.getint('Settings', 'popup_size')
        fullscreen: bool = config.getboolean('Settings', 'fullscreen')
        notif_volume: int = config.getint('Settings', 'notif_volume')
        video_volume: int = config.getint('Settings', 'video_volume')
        popup_count: int = config.getint('Settings', 'popup_count')
    except Exception as err:
        logging.error(repr(err))
        return None
    settings_dict: dict = {"link_id": link_id,
                           "api_key": api_key,
                           "download": download,
                           "save_path": save_path,
                           "time_limit": time_limit,
                           "auto_close": auto_close,
                           "play_video": play_video,
                           "popup_size": popup_size,
                           "fullscreen": fullscreen,
                           "notif_volume": notif_volume,
                           "video_volume": video_volume,
                           "popup_count": popup_count}
    return settings_dict

def write_setting(settings_ini: str, section: str, option: str, var: Any) -> None:
    if not config_read(settings_ini):
        return None
    try:
        config.add_section(section)
    except configparser.DuplicateSectionError:
        pass
        config.set(section, option, str(var))
    try:
        with open(settings_ini, 'w') as file:
            config.write(file)
        logging.debug(f"{option} set to {var}")
    except Exception as err:
        logging.error(f"{repr(err)}\nFailed to save {option} as {var}")
