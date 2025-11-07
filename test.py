from adb_shell.adb_device import AdbDeviceUsb
from adb_shell.exceptions import UsbReadFailedError, UsbDeviceNotFoundError, UsbWriteFailedError
from adb_shell.auth.keygen import keygen
import time
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from os.path import exists
KEY = "./KEY_KEEP_PRIVATE"
print(exists(KEY))
if not exists(KEY):
	keygen(KEY)

with open(KEY) as f:
	_priv = f.read()
with open(KEY+".pub") as f:
	_pub = f.read()
key = PythonRSASigner(_pub, _priv)

waiting_state = "Waiting..."
while True:
	print(waiting_state)
	try:
		device = AdbDeviceUsb()
		device.connect(rsa_keys=[key],auth_timeout_s=1)
		break # If Success
	except UsbDeviceNotFoundError:
		waiting_state="Waiting for Device..."
		time.sleep(1)
	except UsbReadFailedError as e:
		if e.usb_error.value == -7:
			waiting_state="Waiting for Authorization..."
		#print(e.usb_error.value)
	except UsbWriteFailedError as e:
		print("Don't Unplug the Device!")
		time.sleep(1) # Failsafe for no further errors/spam
	except:
		print("General Error...")
