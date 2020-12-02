# esms-detection
## To compile main.exe
pyinstaller --add-data="Detection/haarcascade_frontalface_default.xml;Detection" --add-binary="Detection\Weight\model-epoch-30.h5;Detection\Weight" --onefile --noconsole main.py
## To compile upload.exe
pyinstaller --onefile --noconsole upload.py
## to run main.exe
$env:OPENH264_LIBRARY="D:/Capstone/esms-detection/codec/openh264-1.8.0-win64.dll"; start main.exe
