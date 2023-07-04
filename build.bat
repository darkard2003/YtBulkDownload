call pyenv\Scripts\activate
pyinstaller --onefile ^
    --windowed ^
    --icon=assets/icon.ico ^
    --name=ytdownloader ^
    --add-binary="assets/icon.ico;assets/" ^
    --add-binary="bin/ffmpeg.exe;bin/" ^
    --add-binary="bin/ffprobe.exe;bin/" ^
    main.py