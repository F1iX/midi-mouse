#!/bin/sh
cd /home/pi/midi-mouse
.venv/bin/python3 evdevmidi.py 10.42.0.255 100
#.venv/bin/python3 evdevmidi.py 10.42.1.255 100