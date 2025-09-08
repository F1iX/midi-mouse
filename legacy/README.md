# Legacy code from the early days of midi-mouse

## Remapping mouse buttons to keyboard keys and sending MIDI events
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