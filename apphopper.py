#!/usr/bin/env python3

import argparse
import logging
import re
import subprocess
import sys
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_active_window_id() -> str:
    """
    Gets the hex ID of the currently active window using xdotool.

    Returns:
        str: The window ID in hexadecimal format (e.g., '0x1234567').
    
    Raises:
        RuntimeError: If xdotool fails or returns unexpected output.
    """
    try:
        completed = subprocess.run(
            ["xdotool", "getactivewindow"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
        # xdotool returns decimal, convert to hex for consistency with wmctrl
        id_hex = hex(int(completed.stdout.strip()))
        logger.debug(f"Active window ID: {id_hex}")
        return id_hex
    except (subprocess.CalledProcessError, ValueError) as e:
        logger.error(f"Failed to get active window ID: {e}")
        return "0x0"


def choose_window_id(ids: List[str]) -> str:
    """
    Selects the next window ID to focus based on the currently active window.
    Implements a cycling behavior.

    Args:
        ids: A list of candidate window IDs (hex strings).

    Returns:
        str: The selected window ID.
    """
    if not ids:
        return ""

    active_win_id = get_active_window_id()

    # Convert to decimal for robust comparison (handles leading zeros in hex)
    try:
        active_win_id_decimal = int(active_win_id, base=16)
    except ValueError:
        return ids[0]

    choose_next_id = False
    for window_id in ids:
        if choose_next_id:
            logger.debug(f"Cycling to next window ID: {window_id}")
            return window_id

        try:
            id_decimal = int(window_id, base=16)
            if id_decimal == active_win_id_decimal:
                choose_next_id = True
        except ValueError:
            continue

    # If the active window was the last in the list, or not found, return the first one
    return ids[0]


def get_active_desktop_id() -> str:
    """
    Gets the ID of the currently active desktop using wmctrl.

    Returns:
        str: The desktop index as a string.
    
    Raises:
        RuntimeError: If wmctrl fails or no active desktop is found.
    """
    try:
        completed = subprocess.run(
            ["wmctrl", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get desktops: {e}")
        sys.exit(1)

    # Parse list of desktops for current desktop (marked with '*')
    active_desktop_regex = re.compile(r"^(\d+)\s*\*")
    for line in completed.stdout.splitlines():
        match = active_desktop_regex.search(line)
        if match:
            desktop_id = match.group(1)
            logger.debug(f"Active desktop ID: {desktop_id}")
            return desktop_id

    logger.error("Could not identify the active desktop.")
    sys.exit(1)


def list_windows_on_desktop(desktop_id: str) -> List[tuple]:
    """
    Returns all windows on the specified desktop with their class and title.

    Args:
        desktop_id: The ID of the desktop to list windows on.

    Returns:
        List of (window_id, window_class, window_title) tuples.
    """
    try:
        completed = subprocess.run(
            ["wmctrl", "-l", "-x"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list windows: {e}")
        return []

    # Format: ID  Desktop  Class  Client  Title (title can contain spaces)
    window_line_regex = re.compile(r"^(0x[\da-fA-F]+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)$")
    result = []
    for line in completed.stdout.splitlines():
        match = window_line_regex.match(line)
        if match:
            win_id, win_desktop, win_class, _client, win_title = match.groups()
            if win_desktop == desktop_id:
                result.append((win_id, win_class, win_title.strip()))
    return result


def get_window_ids(window_name: str, desktop_id: str) -> List[str]:
    """
    Returns the IDs of all windows matching the name on the specified desktop.

    Args:
        window_name: Regex pattern or partial string to match against window class.
        desktop_id: The ID of the desktop to search on.

    Returns:
        List[str]: A list of matching window IDs.
    """
    try:
        completed = subprocess.run(
            ["wmctrl", "-l", "-x"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list windows: {e}")
        return []

    # regex to match: ID  Desktop  Class  Host  Title
    # We look for the ID and ensure it's on the right desktop and matches the class
    window_regex_string = rf"^(0x[\da-fA-F]+)\s+{desktop_id}\s+{window_name}"
    window_regex = re.compile(window_regex_string, re.IGNORECASE)

    matched_ids = []
    for line in completed.stdout.splitlines():
        match = window_regex.search(line)
        if match:
            matched_ids.append(match.group(1))

    logger.debug(f"Found {len(matched_ids)} windows matching '{window_name}'")
    return matched_ids


def check_dependencies():
    """Checks if required system tools are installed."""
    for tool in ["wmctrl", "xdotool"]:
        try:
            subprocess.run([tool, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            logger.error(f"Required tool '{tool}' not found. Please install it (e.g., 'sudo apt install {tool}').")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="A 'Run or Raise' utility: Switch between windows of an application, cycle through them, or launch it if not running."
    )
    parser.add_argument(
        "window_name",
        nargs="?",
        help="The name/class of the window to find (e.g., 'Navigator.firefox')."
    )
    parser.add_argument(
        "launch_cmd",
        nargs="?",
        help="Optional command to launch the app if no windows are found."
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all windows on the current desktop with their window classes (for discovering window names)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Check for wmctrl and xdotool before proceeding
    check_dependencies()

    active_desktop_id = get_active_desktop_id()

    if args.list:
        windows = list_windows_on_desktop(active_desktop_id)
        if not windows:
            logger.info("No windows found on the current desktop.")
        else:
            # Use fixed-width columns for readability
            max_class = max(len(w[1]) for w in windows) if windows else 0
            max_class = max(max_class, len("Window class"))
            for win_id, win_class, win_title in windows:
                print(f"{win_class:<{max_class}}  {win_title}")
        sys.exit(0)

    if not args.window_name:
        parser.error("window_name is required when not using --list")
    requested_window_ids = get_window_ids(args.window_name, active_desktop_id)

    if not requested_window_ids:
        if args.launch_cmd:
            logger.info(f"No windows found for '{args.window_name}'. Launching: {args.launch_cmd}")
            try:
                # Use Popen to launch without waiting for it to exit
                subprocess.Popen(args.launch_cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                logger.error(f"Failed to launch command: {e}")
                sys.exit(1)
            sys.exit(0)
        else:
            logger.warning(f"No windows found matching '{args.window_name}' and no launch command provided.")
            sys.exit(0)

    if len(requested_window_ids) == 1:
        target_id = requested_window_ids[0]
    else:
        target_id = choose_window_id(requested_window_ids)
        logger.debug(f"Multiple windows found, selected: {target_id}")

    logger.info(f"Switching to window: {target_id}")
    try:
        subprocess.run(
            ["wmctrl", "-i", "-a", target_id],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to switch to window {target_id}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

