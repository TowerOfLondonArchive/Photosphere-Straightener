# Photosphere Straightener

A simple python script to manually level photosphere images.

Sometimes the images taken by 360 cameras are not automatically
aligned with the horizon, making them difficult to view.

This application allows you to manually adjust the horizon
and bearing to make it viewable.

It embeds the rotation in the exif metadata. It does not re-encode the image.

## Steps to use

1) Install Python
2) Install the requirements in requirements.txt
   1) `pip install -r requirements.txt`
3) Download and extract exiftool into this directory
   1) Download from https://exiftool.org/
   2) Extract the zip into this directory
   3) Rename `exiftool(-k).exe` to `exiftool.exe`
4) Run the script 
   1) `python photosphere_straightener.py path/to/img.jpg`
   2) `python photosphere_straightener.py glob:path/to/*.jpg`
