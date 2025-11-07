# F78Tool
# A Tool for Controlling Fire OS 7/8 Devices
# By Lighty / LightyUwU

#############
# LIBRARIES #
#############
from adb_shell.adb_device import AdbDeviceUsb
from adb_shell.exceptions import (UsbReadFailedError,
                                  UsbDeviceNotFoundError,
                                  UsbWriteFailedError)
from usb1 import USBErrorBusy
from os.path import exists
from config import KEY_FILE_PATH
from adb_shell.auth.keygen import keygen as adb_keygen
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from CTkMessagebox import CTkMessagebox as MsgBox
import customtkinter as ctk
import config
import time, os
from sys import exit

#####################
# KEY LOAD FUNCTION #
#####################
def load_keys():
    # Create new key if any missing
    if not exists(KEY_FILE_PATH):
        adb_keygen(KEY_FILE_PATH)
    if not exists(KEY_FILE_PATH+".pub"):
        adb_keygen(KEY_FILE_PATH)

    # Load Key Files
    with open(KEY_FILE_PATH) as f:
        _private_key = f.read()
    
    with open(KEY_FILE_PATH+".pub") as f:
        _public_key = f.read()

    return PythonRSASigner(_public_key, _private_key)

########################
# DEVICE FIND FUNCTION #
########################
def find_device(key):
    # String for Waiting Info
    _state_string = "Waiting..."
    
    _device = None
    
    while True:
        print(_state_string)
        try:
            time.sleep(0.5)
            _device = AdbDeviceUsb()
            _device.connect(rsa_keys=[key], auth_timeout_s=0.5)
            break
        except UsbDeviceNotFoundError:
            _state_string="Please Connect your Device..."
            #MsgBox(title="ADB", msg=_state_string)
        except UsbReadFailedError as usb_ex:
            if usb_ex.usb_error.value == -7:
                _state_string = "Waiting for Authorization..."
            elif usb_ex.usb_error.value == -8:
                _state_string = "Please Close ADB on your PC! (run: adb kill-server)"
        except USBErrorBusy:
            _state_string = "Please Close ADB on your PC! (run: adb kill-server)"
        except UsbWriteFailedError:
            print("Don't Unplug the Device!")
            #MsgBox(title="Stop!", message="Don't Unplug the Device!", icon="cancel")
        except Exception as e:
            _state_string = "An Error Occurred."
            print(e)
    return _device
            
            
###################
# PAYLOAD HELPERS #
###################
def _uploader(dev):
    dev.push(config.PAYLOAD, "/data/local/tmp/payload.sh")
    dev.shell("sh /data/local/tmp/payload.sh")
    
def upload_payload(dev):
    v = ""
    tries = 0
    while v.strip()!="1":
        if tries > 0:
            print(f"Failed. Retrying ({tries}/10)...")
        if tries > 10:
            print("Failure!")
            print("Please go into your terminal and run: ")
            print("adb shell /data/local/tmp/payload.sh && adb kill-server")
            exit(1)
            break
        print("Uploading...")
        _uploader(dev)
        print("Testing!")
        # Check success (echo 1 was run)
        v = dev.shell("toybox yes 'echo 1' | head -n 1 | toybox nc -q 2 -w 2 localhost 4343")
        tries += 1
    
def sh_payload(dev, command):
    # Fake file for stdin
    with open("fake_file", "w") as f:
        f.write(command)
    dev.push("fake_file", "/data/local/tmp/stdin")
    
    # Execute
    o = dev.shell("cat /data/local/tmp/stdin | toybox nc -q 2 -w 2 localhost 4343")
    
    # Cleanup
    dev.shell("rm /data/local/tmp/stdin")
    os.remove("fake_file")
    
    return o

def kill_payload(dev):
    sh_payload(dev, "killall toybox") # Just kill NC Listen server

debloat_lists = {
    "Minimal":["com.amazon.dee.app","amazon.speech.sim","com.amazon.alexa.multimodal.gemini","com.amazon.comms.kids","com.amazon.weather","com.amazon.csapp","com.ivona.tts.oem"],
    "Regular":["com.amazon.dee.app","amazon.speech.sim","com.amazon.alexa.multimodal.gemini","com.amazon.comms.kids","com.amazon.weather","com.amazon.csapp","com.ivona.tts.oem",
               "com.kingsoft.office.amz","com.amazon.kindle.unifiedSearch","com.amazon.afe.app","com.amazon.cloud9","com.amazon.windowshop","com.android.quicksearchbox","com.amazon.avod","com.amazon.kindle","com.amazon.webapp","com.amazon.cloud9.kids","com.amazon.imdb.tv.mobile.app","com.amazon.redstone","com.audible.application.kindle","com.amazon.venezia","com.amazon.photos","com.amazon.mp3","com.amazon.tahoe","com.amazon.ags.app","com.amazon.hedwig"],
    "Extreme":["com.amazon.dee.app","amazon.speech.sim","com.amazon.alexa.multimodal.gemini","com.amazon.comms.kids","com.amazon.weather","com.amazon.csapp","com.ivona.tts.oem",
               "com.kingsoft.office.amz","com.amazon.kindle.unifiedSearch","com.amazon.afe.app","com.amazon.cloud9","com.amazon.windowshop","com.android.quicksearchbox","com.amazon.avod","com.amazon.kindle","com.amazon.webapp","com.amazon.cloud9.kids","com.amazon.imdb.tv.mobile.app","com.amazon.redstone","com.audible.application.kindle","com.amazon.venezia","com.amazon.photos","com.amazon.mp3","com.amazon.tahoe","com.amazon.ags.app","com.amazon.hedwig",
            "com.amazon.weather","com.android.bookmarkprovider","com.android.calendar","com.android.camera2","com.android.deskclock","com.android.contacts","com.android.providers.downloads.ui","com.android.email","com.android.gallery3d","com.android.protips","com.android.music"],
}

#####################
# ADB & PKG HELPERS #
#####################
_pkg_named = {
    "amazon.fireos":"*Fire OS",
    "android":"*Android",
    "com.amazon.device.software.ota.override":"OTA Override",
    "com.amazon.comms.kids":"Alexa Communication",
    "com.amazon.photos": "Amazon Photos",
    "com.amazon.kindle.otter.oobe.forced.ota":"Forced OTA",
    "com.amazon.venezia":"Amazon Appstore",
    "com.amazon.weather":"Arcus Weather",
    "com.amazon.mp3":"Amazon Music",
    "com.amazon.dee.app":"Alexa",
    "com.amazon.tahoe":"Amazon Kids",
    "com.amazon.alexa.multimodal.gemini":"Alexa Cards",
    "com.android.gallery3d":"Gallery",
    "com.audible.application.kindle":"Audible",
    "com.amazon.device.software.ota":"OTA Updates",
    "com.android.contacts":"Contacts App",
    "com.android.calculator2": "Calculator",
    "com.android.calendar":"Calendar",
    "com.amazon.photos":"Amazon Photos",
    "com.android.camera2":"Camera",
    "com.android.deskclock":"Clock",
    "com.android.providers.downloads.ui":"Downloads UI",
    "com.android.email":"E-Mail",
    "com.amazon.redstone":"Fire Keyboard",
    "com.ivona.tts.oem":"IVONA TTS",
    "com.amazon.imdb.tv.mobile.app":"IMDB",
    "com.amazon.cloud9.kids":"Kids Web Browser",
    "com.amazon.kindle": "Kindle",
    "com.amazon.webapp": "Kindle Store",
    "com.android.music":"Music",
    "com.android.musicfx":"MusicFX",
    "com.amazon.avod":"Prime Video",
    "com.amazon.cloud9":"Silk Browser",
    "com.amazon.windowshop":"Amazon App",
    "com.amazon.afe.app":"Tap to Alexa",
    "com.kingsoft.office.amz":"WPS Office"
}

def pkg_named(s):
    try:
        if _pkg_named[s][0]=="*":
            return (True, _pkg_named[s][1:]+" ("+s+")") # If Should ABSOLUTELY NOT remove
        return (False, _pkg_named[s]+" ("+s+")")
    except KeyError:
        return (False, s)


class Package:
    def __init__(self, dev, pkg,name,enabled):
        self.dev = dev
        self.pkg = pkg
        self.enabled = enabled
        self.name = name
        self.btn = None
        
    def disable(self):
        print(sh_payload(self.dev, "pm disable-user "+self.pkg))
        self.enabled = False
        # Make Button Red
        self.btn_color()
    
    def enable(self):
        print(sh_payload(self.dev, "pm enable "+self.pkg))
        self.enabled = True
        # Make Button Green
        self.btn_color()
        
    def btn_color(self):
        if not self.btn: return
        if self.enabled:
            self.btn.configure(fg_color="Green")
        else:
            self.btn.configure(fg_color="Red")
    
    def toggle(self):
        print("Toggling " + self.name)
        if self.enabled: self.disable()
        else: self.enable()
        
    def assign(self, btn, useable=True):
        self.btn = btn
        if useable:
            self.btn_color()
        
def get_packages(dev):
    _disabled_str = dev.shell("pm list packages -d")
    _enabled_str = dev.shell("pm list packages -e")
    
    _disabled_strs = _disabled_str.split("\n")
    _enabled_strs = _enabled_str.split("\n")
    
    _out_list = []
    
    for string in _disabled_strs:
        s = string.removeprefix("package:").strip()
        is_blocked, name = pkg_named(s)
        if s == "": continue
        if is_blocked:
            _out_list.append(
                Package(dev, name, "*", False)
            )
        else:
            _out_list.append(
                Package(dev, s, name, False)
            ) 
        
    
    for string in _enabled_strs:
        s = string.removeprefix("package:").strip()
        is_blocked, name = pkg_named(s)
        if s == "": continue
        if is_blocked:
            _out_list.append(
                Package(dev, name, "*", True)
            )
        else:
            _out_list.append(
                Package(dev, s, name, True)
            ) 
        
    return sorted(_out_list, key=lambda el: el.pkg)