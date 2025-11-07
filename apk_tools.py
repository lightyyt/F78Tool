# F78Tool
# A Tool for Controlling Fire OS 7/8 Devices
# By Lighty / LightyUwU

#############
# LIBRARIES #
#############
import requests, tempfile, os, zipfile, shutil
from tqdm import tqdm
from pathlib import Path
from CTkMessagebox import CTkMessagebox as MsgBox
######################
# DOWNLOAD FUNCTIONS #
######################

class _App:
    def __init__(self, name, package, apkpure_version_code=-1, is_apkpure=True):
        self.name = name
        if is_apkpure:
            # is latest
            if apkpure_version_code == -1:
                self.url = f"https://d.apkpure.com/b/APK/{package}?version=latest"
            # is version code provided
            else:
                self.url = f"https://d.apkpure.com/b/APK/{package}?versionCode={apkpure_version_code}"
        else:
            self.url = package

class _Pack:
    def __init__(self, packages, depends=[]):
        self.depends = depends
        self.packages=packages

    def install(self):
        pass

packs = {
    "Google Play Services": _Pack([
        _App("Google Account Manager", "com.google.android.gsf.login"),
        _App("Google Services Framework", "com.google.android.gsf", 26),
        _App("Google Play Services", "com.google.android.gms", 252331000)
    ]),
    "Google Play Store": _Pack(depends=["Google Play Services"],
        packages=[
        _App("Play Store", "com.android.vending", 84771900),
        _App("Play Games", "com.google.android.play.games", 551070430)
    ]),
    "Minimal GApps (Chrome, Photos, Google)":  _Pack(depends=["Google Play Services"],
        packages=[
        _App("Chrome", "com.android.chrome", 524912610),
        _App("Photos", "com.google.android.apps.photos", 50709990),
        _App("Google", "com.google.android.googlequicksearchbox", 301233077)
    ]),
    "GBoard": _Pack(depends=["Google Play Services"],
        packages=[
        _App("GBoard", "com.google.android.inputmethod.latin")
    ]),
    "Lawnchair Legacy": _Pack([
        _App("Lawnchair", "ch.deletescape.lawnchair.plah")
    ]),
    "Nova Launcher": _Pack([
        _App("Nova", "com.teslacoilsw.launcher")
    ])
}

installed_packs = []

def install_pack(dev, pack_name, as_dep=False):
    # Just fancy info text
    if as_dep:
        print("Installing Dependency: " + pack_name)
    else:
        print("Installing Pack: " + pack_name)

    # Get Pack info
    pack = packs[pack_name]

    # Scan Dependencies
    for dep in pack.depends:
        # Check if not installed
        if dep not in installed_packs:
            msg = MsgBox(title="Install - "+pack_name,
                         message="This pack requires "+dep+".\nIs it already installed?",
                         option_1="Yes",option_2="No - Install",option_3="No - Don't Install", icon="question")
            resp = msg.get()

            # If User wants to install
            if resp == "No - Install":
                install_pack(dev, dep, as_dep=True)
            # Otherwise, user doesn't want to install
    
    # Install me
    for app in pack.packages:
        download_and_install(dev, app.url, app.name)

    if pack_name not in installed_packs:
        installed_packs.append(pack_name)

def download_and_install(dev, url, app_name):
    _temp_dir = tempfile.mkdtemp()
    
    
    _file_name = os.path.join(_temp_dir, "download.apk")
    print(f"Downloading from {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
    }

    r = requests.get(url, headers=headers, stream=True)
    r.raise_for_status()

    # Download with progress
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024 * 1024  # 1 MB chunks

        with open(_file_name, "wb") as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=app_name
        ) as bar:
            for chunk in r.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

    if not zipfile.is_zipfile(_file_name):
        print("APK Is likely corrupt.")
        return
    
    # Check if file is:
    # FILE
    # -> metadata.json
    # -> *.apk
    # BUT NOT IN ANY SUBDIRECTORIES

    with zipfile.ZipFile(_file_name, "r") as zip:
        # Get all root dir files
        root_files = [f for f in zip.namelist() if "/" not in f]

        # Check for inner APKs
        apks = [f for f in root_files if f.endswith(".apk")]

        # Check if there's metadata
        metadata = "metadata.json" in root_files

        if metadata or len(apks) > 1:
            print("XAPK")
            for f in apks:
                zip.extract(f, _temp_dir)
                
            # Get all APKs
            paths = [os.path.join(_temp_dir, f) for f in apks]
            install_xapk(dev, paths)
            return
    
    print("APK")
    install_apk(dev, _file_name)

    shutil.rmtree(_temp_dir, ignore_errors=True)

def _push_with_progress(dev, local_path, device_path):
    total_size = os.path.getsize(local_path)
    bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Pushing {os.path.basename(local_path)}")

    def progress_callback(device_path, bytes_written, total_bytes):
        bar.n = bytes_written
        bar.refresh()

    dev.push(local_path, device_path, progress_callback=progress_callback)
    bar.n = total_size
    bar.close()

def _apk_install_bg(dev, f):
    dev.shell(f"nohup sh -c 'pm install -r /data/local/tmp/{f}.apk && rm /data/local/tmp/{f}.apk' >/dev/null 2>&1 &")

def install_apk(dev, path):
    print(f"Installing: {path}")
    
    # Push file
    print("\tSending...")
    _push_with_progress(dev, path, "/data/local/tmp/f78download.apk")
    print("\tInstalling...")
    #_apk_install_bg(dev, "f78download.apk")
    print(dev.shell("pm install -r /data/local/tmp/f78download.apk && rm /data/local/tmp/f78download.apk",read_timeout_s=6**20))
    #print("\tDone!")
    

def install_xapk(dev, paths):
    print(f"Installing All: {",".join(paths)}")
    
    print("\tSending...")
    # Push files
    dl_paths = ["/data/local/tmp/f78download_"+Path(f).stem for f in paths]
    for f in paths:
        filename = Path(f).stem
        _push_with_progress(dev, f, "/data/local/tmp/f78download_"+filename+".apk")
    print("\tInstalling...")
    print(dev.shell(f"pm install-multiple -r /data/local/tmp/{' '.join(dl_paths)} && rm /data/local/tmp/f78download*"))