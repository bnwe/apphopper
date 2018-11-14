#!/usr/bin/env python3


import re
import subprocess
import sys


def getActiveDesktop():
    # Get desktops from wmctrl
    completed = subprocess.run(
        ["wmctrl", "-d"], stdout=subprocess.PIPE, universal_newlines=True)

    # returnCode = completed.returncode  # TODO: Handle errors

    desktopStdOut = completed.stdout
    print("Output of wmctrl command:")
    print(desktopStdOut)

    # Parse list of desktops for current desktop
    findDesktopRegex = re.compile(r"(\d)\s*\*")

    matchedDesktopObjects = findDesktopRegex.search(desktopStdOut)
    # numFoundActiveDesktops = len(matchedDesktopObjects.groups())
    # TODO: Handle errors (should be 1)
    activeDesktopAsString = matchedDesktopObjects.group(1)
    print("Active desktop is: " + activeDesktopAsString)
    return activeDesktopAsString


def getRequestedWindowId(windowName, desktopNo):
    print()
    # Get windows from wmctrl
    completed = subprocess.run(
        ["wmctrl", "-l", "-x"],
        stdout=subprocess.PIPE,
        universal_newlines=True)
    # returnCode = completed.returncode  # TODO: Handle errors
    windowsStdOut = completed.stdout
    print(windowsStdOut)

    regexString = r"(0x[\w]+)\s*" + desktopNo + "\s" + windowName
    print("regex string for finding " + windowName + ": " + regexString)
    findWindowRegex = re.compile(regexString, re.IGNORECASE)

    matchedWindowObjects = findWindowRegex.search(windowsStdOut)
    if matchedWindowObjects is None:
        print("ERROR: The window " + windowName +
              " could not be uniquely identified on desktop " + desktopNo)
        return None
    else:
        windowIdAsString = matchedWindowObjects.group(1)
        print("window id:" + windowIdAsString)
        return windowIdAsString


def printUsage():
    print("Usage:")
    print("appswitch appname [appcmd]")


if (len(sys.argv) < 2 or len(sys.argv) > 3):
    printUsage()
    sys.exit(0)

desktopNo = getActiveDesktop()

requestedWindowName = sys.argv[1]
winID = getRequestedWindowId(requestedWindowName, desktopNo)

if winID is None and (len(sys.argv) == 3):
    completed = subprocess.run(
        [sys.argv[2]],
        stdout=subprocess.PIPE,
        universal_newlines=True)
    sys.exit()

print("Now switching to winid " + winID)
completed = subprocess.run(
    ["wmctrl", "-i", "-a", winID],
    stdout=subprocess.PIPE,
    universal_newlines=True)
# returnCode = completed.returncode  # TODO: Handle errors
windowsStdOut = completed.stdout
print(windowsStdOut)
