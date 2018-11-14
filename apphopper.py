#!/usr/bin/env python3


import re
import subprocess
import sys


def get_active_desktop_id():
    # Get desktops from wmctrl
    completed = subprocess.run(
        ["wmctrl", "-d"], stdout=subprocess.PIPE, universal_newlines=True)

    # returnCode = completed.returncode  # TODO: Handle errors

    desktopStdOut = completed.stdout
    print("Output of wmctrl command:")
    print(desktopStdOut)

    # Parse list of desktops for current desktop
    active_desktop_regex = re.compile(r"(\d)\s*\*")

    matched_objects = active_desktop_regex.search(desktopStdOut)
    # numFoundActiveDesktops = len(matched_objects.groups())
    # TODO: Handle errors (numFoundActiveDesktops should be 1)
    active_desktop_id = matched_objects.group(1)
    print("Active desktop is: " + active_desktop_id)
    return active_desktop_id


def get_window_id(window_name, desktop_id):
    print()
    # Get windows from wmctrl
    completed = subprocess.run(
        ["wmctrl", "-l", "-x"],
        stdout=subprocess.PIPE,
        universal_newlines=True)
    # returnCode = completed.returncode  # TODO: Handle errors
    windowsStdOut = completed.stdout
    print(windowsStdOut)

    window_regex_string = r"(0x[\w]+)\s*" + desktop_id + "\s" + window_name
    print("regex string for finding " + window_name + ": " + window_regex_string)
    window_regex = re.compile(window_regex_string, re.IGNORECASE)

    matched_objects = window_regex.search(windowsStdOut)
    if matched_objects is None:
        print("ERROR: The window " + window_name +
              " could not be uniquely identified on desktop " + desktop_id)
        return None
    else:
        window_id = matched_objects.group(1)
        print("window id:" + window_id)
        return window_id


def print_cli_usage():
    print("Usage:")
    print("appswitch appname [appcmd]")


if __name__ == '__main__':
    if (len(sys.argv) < 2 or len(sys.argv) > 3):
        print_cli_usage()
        sys.exit(0)

    active_desktop_id = get_active_desktop_id()

    requested_window_name = sys.argv[1]
    requested_window_id = get_window_id(requested_window_name, active_desktop_id)

    if requested_window_id is None and (len(sys.argv) == 3):
        completed = subprocess.run(
            [sys.argv[2]],
            stdout=subprocess.PIPE,
            universal_newlines=True)
        sys.exit()

    print("Now switching to winid " + requested_window_id)
    completed = subprocess.run(
        ["wmctrl", "-i", "-a", requested_window_id],
        stdout=subprocess.PIPE,
        universal_newlines=True)
    # returnCode = completed.returncode  # TODO: Handle errors
    windowsStdOut = completed.stdout
    print(windowsStdOut)
