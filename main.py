# F78Tool
# A Tool for Controlling Fire OS 7/8 Devices
# By Lighty / LightyUwU

#############
# LIBRARIES #
#############
import tools
from gui.shell import AdbShellWindow
from gui.main import AdbMainWindow
import sys

############
# LOAD KEY #
############

keys = tools.load_keys()

dev = tools.find_device(keys)
if len(sys.argv) == 2:
    if sys.argv[1] == "reboot":
        print("Rebooting Device...")
        dev.reboot()
        exit(1)
        
print("Found!\nThis might take some time now...")
tools.upload_payload(dev)


win = AdbMainWindow(dev)
win.mainloop()

# Fix Device (Mostly)
tools.kill_payload(dev)
#sh = AdbShellWindow(dev)
#sh.mainloop()

