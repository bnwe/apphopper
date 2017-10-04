#!/usr/bin/env python3

# TODOs:
# - CLI arg for program to launch if window not found

# Ideas:
# - let user chose, whether scope is current desktop or all
# - If found window is already current, then toggle to next
#   - wmctrl doesnt know current window. use: CURRENTAPP=` xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2 | awk ' { gsub("0x" , "0x0" ); print $0  } '`
#   - maybe use other programs like xprop: https://www.linuxquestions.org/questions/showthread.php?p=5673363#post5673363
#   - inform about errors via desktop notification

import subprocess
import sys
import re


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
        return
    else:
        windowIdAsString = matchedWindowObjects.group(1)
        print("window id:" + windowIdAsString)
        return windowIdAsString


def printUsage():
    print("Usage:")
    print("appswitch appname [appcmd]")


# TODO Use proper command line arg handling
if(len(sys.argv) < 2 or len(sys.argv) > 3):
    printUsage()
    sys.exit(0)

desktopNo = getActiveDesktop()

requestedWindowName = sys.argv[1]
winID = getRequestedWindowId(requestedWindowName, desktopNo)

print("Now switching to winid " + winID)
completed = subprocess.run(
        ["wmctrl", "-i", "-a", winID],
        stdout=subprocess.PIPE,
        universal_newlines=True)
# returnCode = completed.returncode  # TODO: Handle errors
windowsStdOut = completed.stdout
print(windowsStdOut)
