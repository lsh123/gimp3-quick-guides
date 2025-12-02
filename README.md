# Aleksey Quick Guides - GIMP 3.0 Plugin

A Python plugin for GIMP 3.0+ that provides quick guides configuration

## Installation

### Windows
1. Copy `aleksey_quick_guides.py` to your GIMP 3.0 plugins directory:
   ```
   C:\Users\[YourUsername]\AppData\Roaming\GIMP\3.0\plug-ins\
   ```

2. Make sure the file has execute permissions

3. Restart GIMP

### macOS
1. Copy `aleksey_quick_guides.py` to:
   ```
   ~/Library/Application Support/GIMP/3.0/plug-ins/
   ```

2. Make the file executable:
   ```bash
   chmod +x ~/Library/Application\ Support/GIMP/3.0/plug-ins/aleksey_quick_guides.py
   ```

3. Restart GIMP

### Linux
1. Copy `aleksey_quick_guides.py` to:
   ```
   ~/.config/GIMP/3.0/plug-ins/
   ```

2. Make the file executable:
   ```bash
   chmod +x ~/.config/GIMP/3.0/plug-ins/aleksey_quick_guides.py
   ```

3. Restart GIMP

## Usage:

The plugin is available in the menu bar or the image context menu "Image" > "Guides" > "Quick Guides".
The horizontal and vertical guides would be added / deleted basd on comma separated lists.
