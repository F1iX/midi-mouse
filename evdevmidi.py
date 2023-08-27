import evdev
import mido
import time

DEVICE_NAME = "Logitech Wireless Mouse"
device_path = None

while True:
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name == DEVICE_NAME:
                device_path = device.path

        device = evdev.InputDevice(device_path)
        device.grab()  # become sole recipient of all incoming input events
        outport = mido.open_output()
        scroll_value = 127
        slider_channel = 0

        print("Grabbing {} and sending MIDI commands...".format(DEVICE_NAME))

        for event in device.read_loop():
            if event.code == 272:  # Left mouse button
                if event.value == 1:
                    msg = mido.Message('note_on', note=10)
                    outport.send(msg)
                if event.value == 0:
                    msg = mido.Message('note_off', note=10)
                    outport.send(msg)
            if event.code == 273:  # Right mouse button
                if event.value == 1:
                    msg = mido.Message('note_on', note=12)
                    outport.send(msg)
                if event.value == 0:
                    msg = mido.Message('note_off', note=12)
                    outport.send(msg)
            if event.code == 274:  # Mid mouse button
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
    except Exception as e:
        print(e)
        print("Retrying (consider using sudo or cancel with CTRL+C)...")
    time.sleep(1)