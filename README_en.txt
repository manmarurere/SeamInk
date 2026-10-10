SeamInk - tattoo baker for FFXIV skin textures
=====================================================================

Place a transparent PNG on a 3D body, and SeamInk writes the tattoo into the
right spots of the skin texture.

Skin textures lay the body out in separate pieces (left and right, upper and
lower body, and so on). A design that crosses a seam, such as one around the
navel or down the middle of the back, normally has to be cut up and painted
piece by piece. SeamInk works it out from the 3D body instead, so the design
stays continuous across the seams.

When it starts, it reads your Penumbra settings and loads the body model
(upper and lower body) and skin texture you currently use in game.


== What you need
--------------------------------------------------
- Windows 10 / 11
- XIVLauncher (Dalamud) and Penumbra
- A modded body and skin
  (Bibo+ / RueXB / YAB+ / X-Body Skin and similar. Vanilla bodies and skin are not supported)
- Python 3.8 or later
  Install it from https://www.python.org/downloads/ .
  On the first install screen, make sure to tick "Add python.exe to PATH".
- Chrome or Edge
- An internet connection when it starts (it loads the 3D viewer library)


== Files
--------------------------------------------------
  Start_SeamInk.bat   ... double-click this to start
  seamink.html        ... the tool itself
  seamink_server.py   ... small helper that reads your Penumbra settings and mods (read-only)
  README_en.txt       ... this file
  README_ja.txt       ... the same in Japanese

Keep them together in the same folder.


== First start
--------------------------------------------------
1. If you received a zip, choose "Extract All" first.
   (Double-clicking inside the zip does not work.)
2. Double-click "Start_SeamInk.bat".
   If you see "Windows protected your PC", click "More info" and then "Run anyway".
3. A black window opens, and SeamInk opens in your browser shortly after.
   Keep the black window open while you use the tool.
4. In "Load the body you use in Penumbra" at the top left, choose your
   character's race and gender and press "Load".
   The body and skin appear, and the panel lists which file came from which mod.
   From then on it loads automatically when you start it.
5. Switch the language with "日本語 / English" at the top left.
   Open "How to use" in the tool for a description of every control.


== How to use
--------------------------------------------------
1. Add a tattoo image
   Add a transparent PNG in "3 Tattoos", or drop it straight onto the 3D view
   (it is placed where you drop it). Stack as many as you like.

2. Adjust position and size
   Left-drag on the body to slide the tattoo along the surface.
   Use the sliders for size, rotation and opacity.

     Left-drag on body ......... move the tattoo
     Left-drag on background ... rotate the view (Alt+drag works on the body too)
     Right-drag ................ pan
     Wheel ..................... zoom
     Shift+wheel ............... tattoo size
     Ctrl+wheel ................ tattoo rotation
     Q ......................... toggle Place mode
     Delete .................... delete the selected tattoo

   The Front / Back / Left / Right buttons switch the view.
   "Texture layout" at the bottom right shows where the design lands on the texture.

3. Save
   Press "Save texture as .tex". The browser saves "(original name)_tattoo.tex"
   to your Downloads folder. The tool also shows "Replace", the file inside the
   mod that it should replace.

4. Use it in game
   (1) Copy the file shown under "Replace" somewhere safe as a backup.
   (2) Rename the saved _tattoo.tex to the same name as that file and overwrite it.
   (3) In Penumbra, disable the mod and enable it again.
       If nothing changes, type /penumbra redraw in chat or restart the game.

   To undo, copy your backup back.
   Note: updating or reinstalling that mod brings back the original file and removes the tattoo.


== Handy settings
--------------------------------------------------
- Depth ............. lower it if the design spills onto the arms, crotch or back
- Wrap limit ........ how far the design wraps around the sides; lower keeps it to the front
- Project from view . aims the tattoo straight from your current view
- Mirror copy ....... duplicates it, mirrored, on the other side of the body
- Solid color ....... paints the image in one color (handy for recoloring black line art)
- Blend "Multiply" .. lets the skin's shading show through so the ink looks natural
- Save / Open layout  keeps the tattoo images and positions in a file so you can continue later
- Tattoo only (PNG) . for layering it yourself in an image editor


== Safety
--------------------------------------------------
- It only reads. It never changes your Penumbra settings or mod files
  (you replace the file yourself, as described above).
- It reads only Penumbra's settings files and .mdl / .mtrl / .tex / .png files
  inside your mod folder.
- Everything stays on your PC (127.0.0.1). No images or files are sent anywhere.
  The only internet access is downloading the 3D viewer library (three.js) and the UI fonts.


== Troubleshooting
--------------------------------------------------
* The black window says "Python 3.8 or later was not found"
  -> Install Python (tick "Add python.exe to PATH").
     Afterwards, restart your PC or sign out and back in, then try again.

* The black window opens but the browser does not
  -> Copy the http://127.0.0.1:... address shown in the black window
     into Chrome or Edge.

* "Penumbra's settings folder was not found"
  -> If your Penumbra settings are not under XIVLauncher, start it from a command prompt like this:
       Start_SeamInk.bat --penumbra "...\pluginConfigs\Penumbra"

* "No mod replaces the body model" / "No mod provides the skin material"
  -> No enabled Penumbra mod replaces the body or skin for the race and gender you chose. Check that:
     - the race and gender match your character
     - your body and skin mods are enabled in Penumbra
     - "Set" (below the gender) is the collection your character uses
     Vanilla (unmodded) bodies and skin are not supported.

* The skin looks misaligned on the body
  -> Toggle "Flip UV vertically" in "1 Body model".

* The 3D view is black or empty
  -> Check your internet connection and reload the page.
     If it still does not show, update Chrome / Edge.

* The black window closes immediately
  -> Open a command prompt in the SeamInk folder and run Start_SeamInk.bat
     to read the error message.


== Limitations
--------------------------------------------------
- Vanilla bodies and skin are not supported.
- The saved .tex is uncompressed (B8G8R8A8). A 4K skin texture is about 89 MB.
- Very small areas of the texture (such as the crotch) come out slightly soft.
