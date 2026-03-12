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

import random
from platform import system
from getpass import getuser
from file_utils import find_app_path, read_settings_file

def random_message() -> str:

    rand_roll: int = random.randrange(0, 1000)
    if not rand_roll:
        return "<3"

    rand_roll = random.randrange(0, 10)
    if not rand_roll:
        i: int = random.randrange(0, 15)
        match i:
            case 0:
                return "Monosodium glutamate"
            case 1:
                return "Browse e621.net, it's good for your health!"
            case 2:
                return "Protogens are so cool! I wish robots were real..."
            case 3:
                return "Hey guys, did you know that in terms of male human and..."
            case 4:
                return "Shout out to synth_(vader_san) Gotta be one of my favorite tags"
            case 5:
                return "my paws are big and soft paypal me 20 bucks"
            case 6:
                return "hi guyts"
            case 7:
                return "dude shur.up"
            case 8:
                return "oh my goodness gracious"
            case 9:
                return "could i uhh ummm could i get a :3 in the chat"
            case 10:
                return ":3"
            case 11:
                return ">:3"
            case 12:
                return ">///<"
            case 13:
                return "OwO"
            case 14:
                return "UwU"

    rand_roll = random.randrange(0, 4)
    if not rand_roll:
        i = random.randrange(0, 10)
        match i:
            case 0:
                return f"Hi there {getuser()}!"
            case 1:
                return "Made in Arch btw"
            case 2:
                return "61786F6C6F746C"
            case 3:
                return "beep boop"
            case 4:
                return "You know why you're here..."
            case 5:
                return "Keep up the good vibes!"
            case 6:
                return "I forgot what I was gonna write here"
            case 7:
                return "This thing took way too long to make"
            case 8:
                return "Press Start!"
            case 9:
                return "These messages are random!"

    i = random.randrange(0, 5)
    match i:
        case 0:
            if system() == 'Linux':
                return "Try out the Windows version too!"
            else:
                return "Try out the Linux version too!"
        case 1:
            return f"Total pop-ups: {read_settings_file(find_app_path()[1])["popup_count"]}"
        case 2:
            return f"Welcome back {getuser()}"
        case 3:
            return "Made by AxolHex"
        case 4:
            return "Version 1.0.1"
