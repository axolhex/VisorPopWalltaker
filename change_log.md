# Version 1.0.2

## Major Changes

- New feature: multi-monitor support
    - Added Monitors option to main menu
    - Fullscreen pop-ups now only cover one screen
    - Pop-up windows now scale correctly when using multiple monitors
    - Menus are now correctly centered when using multiple monitors
- Reworked main menu and organized connection and pop-up settings into separate tabs
- Added Polling delay option to main menu
- Added more rare title messages to main menu
- Renamed option "Pop-up time limit" to "Time limit"
- Renamed option "Max pop-up size" to "Maximum size"
- Pressing enter in reply menu's entry will now send the reply
- Fixed an issue that caused reply menu to crash when opening certain posts
- Fixed an issue that caused text to not appear when a slider was set to it's lowest value

# Version 1.0.1

## Major Changes

- New feature: replies
    - Added reply menu
    - Added API key option to main menu
    - Added Reply button to main menu
    - Added Reply button to tray icon
- Menus now use custom color palette instead of default tk colors
- Menu windows now have a minimum size
- Maximum value for pop-up time limit increased from 180 to 300
- Replaced title messages "Now on Windows" and "Now on Linux" with "Total pop-ups:"
- Pop-up windows are no longer resizable while open on Hyprland and other titling window managers
- Fixed an issue that caused client to crash when connecting to a link with no posts
- Fixed an issue that caused client to continue running if main menu unexpectedly closed
- Fixed an issue that caused a blank window to briefly appear when opening a pop-up
- Fixed an issue that caused pop-ups to not appear after temporarily losing connection

# Version 1.0.0

## Initial Release
