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

#!/bin/bash
cd "$(dirname $(realpath "$0"))"

help_message(){
    echo -e "$1\nVisorPop is free open source software licensed under the GNU General Public License version 3.\nView full license terms in the COPYING file or at <https://www.gnu.org/licenses/gpl-3.0.html>.\n\n<https://github.com/axolhex/VisorPopWalltaker>\nThis script creates a Python virtual environment for VisorPop and starts the application."
    echo "  -h, --help          Displays this message and exits"
    echo "  -u, --upgrade       Updates Python dependencies before starting"
    exit
}

quit_script(){
    echo "$1"
    exit
}

echo -e "VisorPop Copyright (C) 2026 AxolHex"

options=("-h" "--help" "-u" "--upgrade")
valid_option=false
for arg in ${options[@]}; do
    [[ "$1" == "$arg" || "$1" == "" ]] && valid_option=true
done
! $valid_option && help_message "\n$1 is an invalid option!\n"
[[ $1 == "-h" || $1 == "--help" ]] && help_message
echo -e "Use '-h' or '--help' for more infomation.\n"

echo "Verifying files..."
app_path=$PWD
[ -d "_internal" ] && app_path="$PWD/_internal"

required_files=("$app_path/assets/AeroCE_TriTone_up.wav" "$app_path/assets/icon.png" "$app_path/data/input_image.conf" "$app_path/data/input_video.conf" "$app_path/src/file_utils.py" "$app_path/src/gui.py" "$app_path/src/popup_player.py" "$app_path/src/reply.py" "$app_path/src/title_message.py" "$app_path/src/tk_utils.py" "$app_path/src/visorpop.py")
for file in ${required_files[@]}; do
    [ -f "$file" ] || quit_script "$file not found!"
done
echo "Application path: $app_path"

python3 --version > /dev/null 2>&1 || quit_script "Please install Python before running this script."
if [ ! -d "$app_path/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$app_path/venv" || quit_script "Could not create virtual environment. Make sure python venv is installed."
fi
source "$app_path/venv/bin/activate"

[[ $1 == "-u" || $1 == "--upgrade" ]] && echo "Updating Python dependencies..." || echo "Checking Python dependencies..."
python3 -m pip install --upgrade pip

dependencies=("mpv" "pillow" "psutil" "pycairo" "PyGObject" "pymediainfo" "pystray" "six" "python-xlib" "requests" "certifi" "charset-normalizer" "idna" "urllib3")
for lib in ${dependencies[@]}; do
    fail_message="$lib not installed!"
    if [[ $1 == "-u" || $1 == "--upgrade" ]]; then
        python3 -m pip install --upgrade $lib || quit_script "$fail_message"
    else
        python3 -m pip show $lib > /dev/null 2>&1 || python3 -m pip install $lib || quit_script "$fail_message"
    fi
    echo "$lib OK"
done

python3 "$app_path/src/gui.py" &
echo -e "\nStarted VisorPop!\nYou can now close this window."

deactivate
exit
