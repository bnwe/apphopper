#!/usr/bin/env python3


import re
import subprocess
import sys

# Selects the first window id from the list that is not the active window's id
def choose_window_id(ids):
    active_win_id = get_active_window_id()

    choose_next_id = False
    for id in ids:
        # Previous id was the current one
        if choose_next_id:
            print('chosen id is: ' + id)
            return id

        # convert to decimal, because hex representation is not unique (leading zeros)
        id_decimal = int(id, base=16)
        active_win_id_decimal = int(active_win_id, base=16)

        if id_decimal == active_win_id_decimal:
            choose_next_id = True
            print('active is: ' + active_win_id)

    # In case the last one in the last was the current one
    return ids[0]


# Gets the id (hex) of the currently active window
def get_active_window_id():
    completed = subprocess.run(
        ["xdotool", "getactivewindow"], stdout=subprocess.PIPE, universal_newlines=True)

    id_hex = hex(int(completed.stdout))
    print("id of active window: " + id_hex)
    return id_hex


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


# Returns the IDs of all windows found matching the name on this desktop
def get_window_ids(window_name, desktop_id):
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

        matched_ids = window_regex.findall(windowsStdOut)
        print("matched IDs: ")
        print(matched_ids)
        return matched_ids


def print_cli_usage():
    print("Usage:")
    print("appswitch appname [appcmd]")


if __name__ == '__main__':
    if (len(sys.argv) < 2 or len(sys.argv) > 3):
        print_cli_usage()
        sys.exit(0)

    active_desktop_id = get_active_desktop_id()

    requested_window_name = sys.argv[1]
    requested_window_ids = get_window_ids(requested_window_name, active_desktop_id)

    # app is not open, so run command if given
    if requested_window_ids is None and (len(sys.argv) == 3):
        completed = subprocess.run(
            [sys.argv[2]],
            stdout=subprocess.PIPE,
            universal_newlines=True)
        sys.exit()

    if(len(requested_window_ids) == 1):
        target_id = requested_window_ids[0]
        print("Only one ID found: " + target_id)
    else:
        target_id = choose_window_id(requested_window_ids)
        print("Found " + str(len(requested_window_ids)) + " IDs. Target: " + target_id)

    print("Now switching to winid " + target_id)
    completed = subprocess.run(
        ["wmctrl", "-i", "-a", target_id],
        stdout=subprocess.PIPE,
        universal_newlines=True)
    # returnCode = completed.returncode  # TODO: Handle errors
    windowsStdOut = completed.stdout
    print(windowsStdOut)
