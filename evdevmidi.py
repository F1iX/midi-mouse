import evdev
import mido

DEVICE_NAME = "Logitech Wireless Mouse"
device_path = None

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if device.name == DEVICE_NAME:
        device_path = device.path

device = evdev.InputDevice(device_path)
outport = mido.open_output()
scroll_value = 127
slider_channel = 3

for event in device.read_loop():
    # print(event)
    if event.code == 2:  # Left mouse button
        if event.value == 1:
            msg = mido.Message('note_on', note=10)
            outport.send(msg)
        if event.value == 0:
            msg = mido.Message('note_off', note=10)
            outport.send(msg)
    if event.code == 3:  # Right mouse button
        if event.value == 1:
            msg = mido.Message('note_on', note=12)
            outport.send(msg)
        if event.value == 0:
            msg = mido.Message('note_off', note=12)
            outport.send(msg)
    if event.code == 4:  # Mid mouse button
        if event.value == 1:
            msg = mido.Message('note_on', note=11)
            outport.send(msg)
        if event.value == 0:
            msg = mido.Message('note_off', note=11)
            outport.send(msg)
    if event.code == 11:
        if event.value == 120:  # Scroll up
            scroll_value += 5
            if scroll_value > 127:
                scroll_value = 127
            msg = mido.Message('control_change', value=scroll_value, channel=slider_channel)
            outport.send(msg)
        if event.value == -120:  # Scroll down
            scroll_value -= 5
            if scroll_value < 0:
                scroll_value = 0
            msg = mido.Message('control_change', value=scroll_value, channel=slider_channel)
            outport.send(msg)