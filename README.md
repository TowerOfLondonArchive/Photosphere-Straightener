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
5) Press `j` to look left 90 degrees (or `l` to look right)
6) Press `z` and/or `c` to align the horizontal red line with the horizon
7) Press `h` to reset the temporary look rotation
8) Press `a` and/or `d` to align the horizontal red line with the horizon
9) Press `h` to reset the temporary look rotation
10) Press `q` and/or `e` to align the vertical red line with north (or where you want the image to open)
11) Close the window to save the changes

## Controls

- Left mouse-click and drag to look left and right.
- `j` and `l` to look left and right 90 degrees.
- `h` to reset the temporary look rotation.
- `r` to reset all transforms to 0
- `z` and `c` to increment and decrement the pitch
- `a` and `d` to increment and decrement the roll
- `q` and `e` to increment and decrement the heading

The controls can be configured by editing the script. See line 199+.
