# Apphopper

Apphopper is a "Run or Raise" utility for Linux desktops. It streamlines your workflow by combining application launching and window switching into a single command. 

### How it works:
1.  **Run**: If the application is not running, Apphopper will launch it.
2.  **Raise**: If the application is running but not focused, Apphopper will bring its window to the foreground.
3.  **Cycle**: If a window of the application is already focused, Apphopper will cycle to the next window of that same application (if multiple windows are open on the current desktop).

## Dependencies

- `wmctrl`
- `xdotool`

On Debian/Ubuntu-based systems, you can install these with:
```bash
sudo apt install wmctrl xdotool
```

## Installation

Simply download `apphopper.py` and make it executable:

```bash
chmod +x apphopper.py
```

You can then move it to a directory in your PATH, such as `~/bin` or `/usr/local/bin`.

### Adding apphopper.py to your PATH

To run `apphopper` from anywhere without moving the script, add its directory to your PATH. From the directory containing `apphopper.py`, run:

```bash
echo 'export PATH="$PATH:'$(pwd)'"' >> ~/.bashrc
```

Use `~/.zshrc` instead of `~/.bashrc` if you use zsh. Then run `source ~/.bashrc` (or `source ~/.zshrc`) or open a new terminal.

## Usage

### Command Line

```bash
apphopper <window_class> [launch_command] [-v]
```

- `window_class`: The class of the window to find (e.g., `Navigator.firefox`, `code.Code`).
- `launch_command`: (Optional) The command to run if no windows are found.
- `-v`, `--verbose`: Enable verbose logging for debugging.

### Finding the Window Class

To find the correct window class to use:
1. Open the application you want to target.
2. Run `wmctrl -l -x` in your terminal.
3. Look for your application in the list. The third column contains the class name (e.g., `Navigator.firefox`).

### Setting up a Keyboard Shortcut

For the best experience, bind Apphopper to a keyboard shortcut:

1. Open your desktop's keyboard shortcut settings (e.g., "Keyboard Shortcuts" in Ubuntu/GNOME).
2. Create a new custom shortcut.
3. Set the command to: `apphopper Navigator.firefox firefox`
4. Assign a key combination (e.g., `Super+F`).

Now, pressing `Super+F` will focus Firefox if it's open (cycling through multiple windows if applicable) or launch it if it's closed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
