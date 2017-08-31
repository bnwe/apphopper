#!/usr/bin/env python3

import subprocess

completed = subprocess.run(
    ["wmctrl", "-d"], stdout=subprocess.PIPE, universal_newlines=True)

returnCode = completed.returncode  # TODO: Handle errors

print(type(completed.stdout))
print()
print(completed.stdout)
