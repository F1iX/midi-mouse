# Map mouse/keyboard to MIDI

Python scripts to map keyboard events and/or mouse buttons to MIDI messages in Linux, e.g., for use in QLC+.

## Prerequisites
- Linux
- `evtest`
- Python
- Python packages `mido`, `rtmidi` and `python-rtmidi` (e.g., via pip or AUR packages `python-mido` and `python-rtmidi`, requires `libasound2-dev` and `libjack-dev`)

## Capturing mouse buttons and sending MIDI events
This method captures mouse events with `evdev` and sends MIDI events. Thanks to python-evdev's `grab` method, the mouse will be disabled while the script is running in order not to disturb other programs.
1. Run `sudo evtest` and select your desired device
1. Remember the input device name
1. Adapt `MOUSE_NAME` according to your setup and run `python evdevmidi.py`

## Using MIDI messages in QLC+
1. (Re-) Start QLC+ after running `evdevmidi.py`
1. Activate "RtMidi output" as Input in the Inputs/Outputs tab
![QLC+ MIDI input](docs/qlcp-midi-input.png)
1. Select Profile "None"
1. Register External Input in the properties of a button in your Virtual Console
1. Enjoy strobe, fog and more with your mouse on the dancefloor!

## Autostart
Create `~/.config/autostart/evdevmidi.desktop` with the following content with the path adjusted to your setup to start the script upon bootup:
```
[Desktop Entry]
Type=Application
Name=evdevmidi
Exec=python <path-to-midi-mouse>/evdevmidi.py
StartupNotify=false
```

## Legacy: Remapping mouse buttons to keyboard keys and sending MIDI events
This method is particularily usefull if you would like to use a mouse on a system that is used for other purposes such as djing at the same time such that the mouse should not move and click on things randomly.

### Remapping of mouse buttons to keyboard keys
Remap your mouse buttons to keyboard key events according to [this](https://askubuntu.com/a/1145638/795463) post:
1. Run `sudo evtest` and select your desired device
1. Remember the first few rows, in which the output should look like
    ```
    Input device ID: bus 0x3 vendor 0x46d product 0x4054 version 0x111
    Input device name: "Logitech Wireless Mouse"
    ```
1. Hit the buttons you want to remap. The output should look like
    ```
    Event: time 1692904552.423840, type 4 (EV_MSC), code 4 (MSC_SCAN), value 90001
    Event: time 1692904552.423840, type 1 (EV_KEY), code 272 (BTN_LEFT), value 0
    Event: time 1692904552.423840, -------------- SYN_REPORT ------------
    Event: time 1692904553.063921, type 4 (EV_MSC), code 4 (MSC_SCAN), value 90002
    Event: time 1692904553.063921, type 1 (EV_KEY), code 273 (BTN_RIGHT), value 1
    ```
1. Create a new file `/etc/udev/hwdb.d/99-mouse-remap.hwdb` with

    ```
    evdev:input:b[bustype]v[vendor]p[product]e[version]*
     ID_INPUT_KEY=1
     KEYBOARD_KEY_[msc-scancode]=[desired-key]
     KEYBOARD_KEY_[msc-scancode]=[desired-key]
     KEYBOARD_KEY_[msc-scancode]=[desired-key]
    ```
    1. Replace `[bustype]`, `[vendor]`, `[product]` and `[version]` with the values from the output of the second command with letters converted to uppercase
    1. Replace `[msc-scancode]` with the scancodes in the output of the third step converted to lowercase
    1. Make sure `evdev:` has no preceding space and `ID_INPUT_KEY` and `KEYBOARD_KEY` have excactly one preceding space
1. The resulting file could look like
    ```
    evdev:input:b0003v046Dp4054e0111*
     ID_INPUT_KEY=1
     KEYBOARD_KEY_90001=1
     KEYBOARD_KEY_90002=2
     KEYBOARD_KEY_90003=3
    ```
1. Now run `sudo systemd-hwdb update` and reboot (or run `sudo udevadm control --reload-rules && sudo udevadm trigger`)

### Capturing keyboard events and sending MIDI messages
Adapt `MOUSE_NAME` and `MAPPING` variables according to your setup and run `midiremap.py`

## Credits/Ressources
- https://askubuntu.com/a/1145638/795463
- https://unix.stackexchange.com/a/171583/310042
- https://wiki.archlinux.org/title/Map_scancodes_to_keycodes