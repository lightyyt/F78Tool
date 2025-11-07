# F78Tool
# A Tool for Controlling Fire OS 7/8 Devices
# By Lighty / LightyUwU

#############
# LIBRARIES #
#############
import tools
from gui.shell import AdbShellWindow
from gui.main import AdbMainWindow


############
# LOAD KEY #
############
keys = tools.load_keys()

dev = tools.find_device(keys)
print("Found!\nThis might take some time now...")
tools.upload_payload(dev)


win = AdbMainWindow(dev)
win.mainloop()

# Fix Device (Mostly)
tools.kill_payload(dev)
#sh = AdbShellWindow(dev)
#sh.mainloop()

