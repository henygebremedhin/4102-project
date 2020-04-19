# Real-time Optical Tracking for Garrys Mod

This software uses computer vision ideals to detect and track visuals in the video game Garrys Mod

## Installation

To run this code you will need to install all dependencies using the batch file (installLibs.bat) provided, as well as the Tesseract
OCR engine at this link: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20200328.exe.

Next you must insert the provided file, "ClientScheme.res" into the game files of Gmod. This customizes the hud and turns the background black so Tesseract
can recognize the numbers properly.

Lastly you must grab your path to Tesseract.exe, this is almost always in the same place "C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe".
Replace 'USER' with your current computers USER and copy it onto line 82 of the code. If by any chance the file was installed elsewhere you must find the path and replace
it appropriately.


## Testing

There are 3 main events to test in this program

### Event 1 - Optical Tracking

To do an ideal tracking scenario we spawn one enemy from the Garry’s Mod (Gmod) menu which are Prison Guard, and Prison Shotgun Guard. The ideal situation also called for added commands placed into the Gmod console:
The first will turn off the violence and the second will turn off weapon models for simplicity  Make sure you have your weapon equipped before continuing.

violence_ablood 0, violence_agibs 0, violence_hblood 0, violence_hgibs 0, r_drawviewmodel 0

- Spawn enemies with the menu
- Hold (q) and on the top drop down menu next to (drawing) you will find the (NPC’s) menu , you must make sure to check “ignore players” is on
- Hold (q) and navigate to the (NPC’s) menu button with the money face and click on (combine)
- Select enemies Prison Guard, and Prison Shotgun Guard to spawn at you location, one is fine
- Alt-tab out of the game, start THE SCRIPT and alt-tab back into the game
- Now click the middle mouse button and your mouse should track the nearest enemy

### Event 2 - Low Health

In this event the character must take damage until its Health points reaches a number below 40. Once this is achieved, keyboard presses for SHIFT and 'S' will be
activated and the character will begin sprinting backwards.

### Event 3 - Auto Reload

Last event is when the characters ammo count reaches a number below 3, then the gun will automatically reload.
*this only works on select weapons, including but not limited too. The revolver, pistol and shotgun*

## Framework used

### Built with
- Tesseract

## Authors

Mohamad-Salim Merhi - 100977984

Nazimul Hoque - 100974599

Jonathan Lim - 100937925

Henok Gebremedhin - 100982033

## Credits

name: Hodka

published: May 5, 2014

title: Simulate Python keypresses for controlling a game

link: https://stackoverflow.com/questions/14489013/simulate-python-keypresses-for-controlling-a-game
