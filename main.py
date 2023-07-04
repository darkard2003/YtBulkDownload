import os
import sys
from ui import MainApp


def get_asset(asset_name):
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        return os.path.join(sys._MEIPASS, asset_name) # type: ignore
    else:
        # Running from a script
        return os.path.join(os.path.dirname(__file__), asset_name)

def main():
    icon = get_asset("assets/icon.ico")
    ffmpeg_location = get_asset("bin/ffmpeg.exe")
    app = MainApp(icon=icon, ffmpeg_path=ffmpeg_location)
    app.run()
    os._exit(0)


if __name__ == "__main__":
    main()
