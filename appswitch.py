#!/usr/bin/env python3

import subprocess
import re

# Get desktops from wmctrl
completed = subprocess.run(
    ["wmctrl", "-d"], stdout=subprocess.PIPE, universal_newlines=True)

returnCode = completed.returncode  # TODO: Handle errors

desktopStdOut = completed.stdout
print("Output of wmctrl command:")
print(desktopStdOut)

# Parse list of desktops for current desktop
findDesktopRegex = re.compile(r"(\d)\s*\*")

matchedDesktopObjects = findDesktopRegex.search(desktopStdOut)
numFoundActiveDesktops = len(matchedDesktopObjects.groups())
# TODO: Handle errors (should be 1)
activeDesktopAsString = matchedDesktopObjects.group(1)
print("Active desktop is: " + activeDesktopAsString)
