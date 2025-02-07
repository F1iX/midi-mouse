import evdev
import mido
import time
import socket

DEVICE_NAME = None
with open( "DEVICE_NAME") as file:
    for line in file:
        text = line.rstrip()
        print(text)
        if text[0] != "#":
            DEVICE_NAME = text

ARTNET_OUT_IP = "10.42.0.190"
ARTNET_UNIVERSE = 0
device_path = None

def sendArtNetPacket( universeId, dmxData, artNetSocket ):
    dmxDataLength = len(dmxData)
    packetBytes = bytearray( 18 + dmxDataLength )
    packetBytes[0:6] = b"Art-Net"
    packetBytes[8:9] = b"\x00\x50" # ArtDMX
    packetBytes[11] = 14 # version
    packetBytes[14:16] = universeId.to_bytes( 2, "little" )
    packetBytes[16:18] = dmxDataLength.to_bytes( 2, "big" )
    packetBytes[18:] = dmxData
    artNetSocket.sendall( packetBytes )

while True:
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        print("List of available devices, waiting for \"{}\":".format(DEVICE_NAME))
        for device in devices:
            print(device.name)
            if device.name == DEVICE_NAME:
                device_path = device.path

        device = evdev.InputDevice(device_path)
        device.grab()  # become sole recipient of all incoming input events
        
        outport = mido.open_output()
        
        if ARTNET_OUT_IP:
            artNetOutInterfaceIP = "0.0.0.0"
            artNetUdpPort = 6454
            artNetSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
            artNetSocket.setblocking( False )
            artNetSocket.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )
            artNetSocket.bind( ( artNetOutInterfaceIP, artNetUdpPort+1 ) )
            while True:  # until connected
                try:
                    artNetSocket.connect( ( ARTNET_OUT_IP, artNetUdpPort ) )
                except Exception as e:
                    print(e)
                    print("Retrying to connect for ArtNet in 3s...")
                    time.sleep(3)
                    continue
                else:
                    break
            print( f"Sending Art-Net packets to {ARTNET_OUT_IP}:{artNetUdpPort}" )

        scroll_value = 127
        max_scroll_value = 127
        config_mode = False
        slider_channel = 0

        print("Grabbing {} and sending MIDI/ArtNet commands...".format(DEVICE_NAME))

        dmxData = [0,0,0,0]  # Mouse: [left button, right button, middle button, scrolwheel]

        loop = 0
        config_mode_changed_at_loop = 0
        for event in device.read_loop():
            if event.code == 272:  # Left mouse button
                if event.value == 1:
                    msg = mido.Message('note_on', note=10)
                    outport.send(msg)
                    dmxData[0] = 255
                    if artNetSocket:
                        sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )
                if event.value == 0:
                    msg = mido.Message('note_off', note=10)
                    outport.send(msg)
                    dmxData[0] = event.value
                    if artNetSocket:
                        sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )
            if event.code == 273:  # Right mouse button
                if event.value == 1:
                    msg = mido.Message('note_on', note=12)
                    outport.send(msg)
                    dmxData[1] = 255
                    if artNetSocket:
                        sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )
                if event.value == 0:
                    msg = mido.Message('note_off', note=12)
                    outport.send(msg)
                    dmxData[1] = event.value
                    if artNetSocket:
                        sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )
            if event.code == 274:  # Mid mouse button
                if event.value == 1:
                    msg = mido.Message('note_on', note=11)
                    outport.send(msg)
                    dmxData[2] = 255
                    if artNetSocket:
                        sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )
                if event.value == 0:
                    msg = mido.Message('note_off', note=11)
                    outport.send(msg)
                    dmxData[2] = event.value
                    if artNetSocket:
                        sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )
            if event.code == 11:
                if event.value == 120:  # Scroll up
                    scroll_value += 5
                    if config_mode:
                        max_scroll_value = scroll_value
                    if scroll_value > 127:
                        scroll_value = 127
                    elif scroll_value > max_scroll_value:
                        scroll_value = max_scroll_value
                    msg = mido.Message('control_change', value=scroll_value, channel=slider_channel)
                    outport.send(msg)
                    dmxData[3] = int(scroll_value / 127 * 255)
                    if artNetSocket:
                        sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )
                if event.value == -120:  # Scroll down
                    scroll_value -= 5
                    if scroll_value < 0:
                        scroll_value = 0
                    if config_mode:
                        max_scroll_value = scroll_value
                    msg = mido.Message('control_change', value=scroll_value, channel=slider_channel)
                    outport.send(msg)
                    dmxData[3] = int(scroll_value / 127 * 255)
                    if artNetSocket:
                        sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )
            if dmxData[0] == 255 and dmxData[1] == 255 and dmxData[2] == 255:  # toggle config mode (adjust max scroll value)
                print("{} {}".format(loop,config_mode_changed_at_loop))
                if loop > config_mode_changed_at_loop + 2:  # at least one frame in between
                    if config_mode:
                            config_mode = False
                            print("Leaving config mode (all buttons pressed), max. scrolling value set to {}".format(max_scroll_value))
                    else:
                        config_mode = True
                        print("Entering config mode (all buttons pressed), please select max. scrolling value")
                    config_mode_changed_at_loop = loop
            loop += 1
    except Exception as e:
        print(e)
        print("Retrying (consider using sudo or cancel with CTRL+C)...")
    time.sleep(1)