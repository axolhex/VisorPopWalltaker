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
from datetime import datetime

def setup_logging() -> None:
    logs_path = find_app_path()
    if not os.path.isdir(f'{logs_path[0]}/logs'):
        os.mkdir(f'{logs_path[0]}/logs')
    logging.basicConfig(level=logging.INFO,
                        filename=f'{logs_path[0]}/logs/{datetime.today().strftime("%d-%m-%Y")}.log',
                        format='%(asctime)s [%(levelname)s] — %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S')

#Determines if running as script or executable and returns app's and settings file's path
def find_app_path() -> tuple[str, str]:
    if getattr(sys, 'frozen', False):
        os.environ["REQUESTS_CA_BUNDLE"] = f'{os.path.dirname(__file__)}/certifi/cacert.pem'
        app = str(os.path.dirname(__file__))
        settings = f'{os.path.dirname(sys.executable)}/settings.ini'
    else:
        app = str(os.path.split(os.path.dirname(__file__))[0])
        settings = f'{str(os.path.split(os.path.dirname(__file__))[0])}/settings.ini'
    return app, settings

def write_default_settings(settings_ini: str) -> None:
    config = configparser.ConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'link_id', "")
    config.set('Settings', 'download', "False")
    config.set('Settings', 'save_path', "")
    config.set('Settings', 'auto_close', "True")
    config.set('Settings', 'play_video', "True")
    config.set('Settings', 'time_limit', "60")
    config.set('Settings', 'popup_size', "50")
    config.set('Settings', 'fullscreen', "False")
    config.set('Settings', 'notif_volume', "75")
    config.set('Settings', 'video_volume', "50")
    try:
        with open(settings_ini, 'w') as file:
            config.write(file)
        logging.info(f"Created settings file: {settings_ini}")
    except Exception as err:
        logging.error(f"{repr(err)}\nFailed to write default settings")
        sys.exit()

#Returns all settings as dictionary
def read_settings_file(settings_ini: str) -> dict[str, str | bool | int] | None:
    config = configparser.ConfigParser()
    try:
        config.read(settings_ini)
    except Exception as err:
        logging.error(f"{repr(err)}\nFailed to read: {settings_ini}")
        return None
    try:
        link_id = config.get('Settings', 'link_id')
        download = config.getboolean('Settings', 'download')
        save_path = config.get('Settings', 'save_path')
        auto_close = config.getboolean('Settings', 'auto_close')
        play_video = config.getboolean('Settings', 'play_video')
        time_limit = config.getint('Settings', 'time_limit')
        popup_size = config.getint('Settings', 'popup_size')
        fullscreen = config.getboolean('Settings', 'fullscreen')
        notif_volume = config.getint('Settings', 'notif_volume')
        video_volume = config.getint('Settings', 'video_volume')
    except (configparser.NoSectionError, configparser.NoOptionError) as err:
        logging.error(repr(err))
        return None
    settings_dict = {"link_id": link_id,
                     "download": download,
                     "save_path": save_path,
                     "auto_close": auto_close,
                     "play_video": play_video,
                     "time_limit": time_limit,
                     "popup_size": popup_size,
                     "fullscreen": fullscreen,
                     "notif_volume": notif_volume,
                     "video_volume": video_volume}
    return settings_dict
