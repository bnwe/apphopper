#! python3

import subprocess

completed = subprocess.run(["wmctrl", "-d"], stdout=subprocess.PIPE)

print(type(completed.stdout))
print()
print(completed.stdout)
