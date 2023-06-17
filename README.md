# Map mouse/keyboard to MIDI

Python script to map keyboard events and/or mouse buttons to MIDI messages in Linux, e.g., for use in QLC+.

## Prerequisites
- Linux
- `evtest`
- Python
- Python packages `mido` and `rtmidi` (e.g., via AUR packages `python-mido` and `python-rtmidi`)

## Remap mouse buttons to keyboard keys
Remap your mouse buttons to keyboard key events according to [this](https://askubuntu.com/a/1145638/795463) post.
The new file `/etc/udev/hwdb.d/99-mouse-remap.hwdb` could look like this:
```
evdev:input:b0003v046Dp4054e0111*
 ID_INPUT_KEY=1
 KEYBOARD_KEY_90001=1
 KEYBOARD_KEY_90002=2
 KEYBOARD_KEY_90003=3
```
## Capture keyboard events and send MIDI messages
Adapt `MOUSE_NAME` and `MAPPING` variables according to your setup and run `midiremap.py`

## Use MIDI messages in QLC+
1. (Re-) Start QLC+ after running `midiremap.py`
1. Activate "RtMidi output" as Input in the Inputs/Outputs tab
![QLC+ MIDI input](docs/qlcp-midi-input.png)
1. Select Profile "None"
1. Register External Input in the properties of a button in your Virtual Console
1. Enjoy strobe, fog and more with your mouse on the dancefloor!

## Credits/Ressources
- https://askubuntu.com/a/1145638/795463
- https://unix.stackexchange.com/a/171583/310042
- https://wiki.archlinux.org/title/Map_scancodes_to_keycodes