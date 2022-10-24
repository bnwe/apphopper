# App switching script for linux desktops
## What's this?
A Python script that will set the currently focused windows to a specific window. Optionally the corresponding app can be opened in case the window is not found.

## Usage
To set a keyboard shortcut to an app like firefox:

1. Place the apphopper dir into e.g. `~/bin`
2. Open the app then run in terminal: `wmctrl -l -x`
3. Find the app in the resulting list and copy the name, e.g. `Navigator.firefox`
4. Create a system shortcut (in Ubuntu Mate use the "Keyboard Shortcuts" App or use gsettings) which will call `apphopper.py Navigator.firefox`
