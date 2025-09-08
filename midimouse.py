import evdev
import mido
import time
import socket
import sys

ARTNET_OUT_IP = "10.42.0.255"
ARTNET_UNIVERSE = 0

left_dmx = 0
mid_dmx = 1
right_dmx = 2
scroll_dmx = 3
config_value_dmx = 4
left_config_dmx = 5
mid_config_dmx = 6
right_config_dmx = 7

argstring = "[ARTNET_OUT_IP] [ARTNET_UNIVERSE] [LEFT_DMX] [MID_DMX] [RIGHT_DMX] [SCROLL_DMX] [CONFIG_VALUE_DMX] [LEFT_CONFIG_DMX] [MID_CONFIG_DMX] [RIGHT_CONFIG_DMX]"
if ( len(sys.argv) >= 3 ):
    ARTNET_OUT_IP = sys.argv[1]
    try:
        ARTNET_UNIVERSE = int(sys.argv[2])
        if ARTNET_UNIVERSE > 127:
            print("Warning, Art-Net universes greater than 127 may not work with QLC+!")
        if ( len(sys.argv) >= 4 ):
            left_dmx = int(sys.argv[3]) - 1
        if ( len(sys.argv) >= 5 ):
            mid_dmx = int(sys.argv[4]) - 1
        if ( len(sys.argv) >= 6 ):
            right_dmx = int(sys.argv[5]) - 1
        if ( len(sys.argv) >= 7 ):
            scroll_dmx = int(sys.argv[6]) - 1
        if ( len(sys.argv) >= 8 ):
            config_value_dmx = int(sys.argv[7]) - 1
        if ( len(sys.argv) >= 9 ):
            left_config_dmx = int(sys.argv[8]) - 1
        if ( len(sys.argv) >= 10 ):
            mid_config_dmx = int(sys.argv[9]) - 1
        if ( len(sys.argv) >= 11 ):
            right_config_dmx = int(sys.argv[10]) - 1
        if (min(left_dmx, mid_dmx, right_dmx, scroll_dmx, config_value_dmx, left_config_dmx, mid_config_dmx, right_config_dmx) < 0 or
            max(left_dmx, mid_dmx, right_dmx, scroll_dmx, config_value_dmx, left_config_dmx, mid_config_dmx, right_config_dmx) > 511):
            print( "Error: DMX channel numbers must be between 1 and 512" )
            print( f"Usage: python3 {sys.argv[0]} {argstring}" )
            exit(1)
    except Exception as e:
        print( "Error parsing parameter" )
        print(e)
        print( f"Usage: python3 {sys.argv[0]} {argstring}" )
        exit(1)
else:
    print( "Error parsing parameter")
    print( f"Usage: python3 {sys.argv[0]} {argstring}" )
    exit(1)

DEVICE_NAME = None
with open( "DEVICE_NAME") as file:
    for line in file:
        text = line.rstrip()
        if text[0] != "#":
            DEVICE_NAME = text

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
        print("List of available devices, waiting for {} as defined in file DEVICE_NAME:".format(DEVICE_NAME))
        for device in devices:
            print("\t{}".format(device.name))
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
            print( f"Sending Art-Net packets to Universe {ARTNET_UNIVERSE} at {ARTNET_OUT_IP}:{artNetUdpPort}" )

        scroll_value = 127
        scroll_config_value = 127
        config_mode = False
        slider_channel = 0

        print("Grabbing {} and sending MIDI/ArtNet commands...".format(DEVICE_NAME))

        dmxData = [0] * (max(left_dmx, mid_dmx, right_dmx, scroll_dmx, config_value_dmx, left_config_dmx, mid_config_dmx, right_config_dmx) + 1)
        dmxData[left_dmx] = 0
        dmxData[mid_dmx] = 0
        dmxData[right_dmx] = 0
        dmxData[scroll_dmx] = scroll_value
        dmxData[config_value_dmx] = scroll_config_value
        dmxData[left_config_dmx] = 0
        dmxData[mid_config_dmx] = 0
        dmxData[right_config_dmx] = 0

        loop = 0
        config_mode_changed_at_loop = 0
        for event in device.read_loop():
            if event.code == 272:  # Left mouse button
                if event.value == 1:
                    msg = mido.Message('note_on', note=10)
                    outport.send(msg)
                    dmxData[left_dmx] = 255
                    dmxData[left_config_dmx] = int(scroll_config_value / 127 * 255)
                if event.value == 0:
                    msg = mido.Message('note_off', note=10)
                    outport.send(msg)
                    dmxData[left_dmx] = 0
                    dmxData[left_config_dmx] = 0
            if event.code == 273:  # Right mouse button
                if event.value == 1:
                    msg = mido.Message('note_on', note=12)
                    outport.send(msg)
                    dmxData[right_dmx] = 255
                    dmxData[right_config_dmx] = int(scroll_config_value / 127 * 255)
                if event.value == 0:
                    msg = mido.Message('note_off', note=12)
                    outport.send(msg)
                    dmxData[right_dmx] = 0
                    dmxData[right_config_dmx] = 0
            if event.code == 274:  # Mid mouse button
                if event.value == 1:
                    msg = mido.Message('note_on', note=11)
                    outport.send(msg)
                    dmxData[mid_dmx] = 255
                    dmxData[mid_config_dmx] = int(scroll_config_value / 127 * 255)
                if event.value == 0:
                    msg = mido.Message('note_off', note=11)
                    outport.send(msg)
                    dmxData[mid_dmx] = 0
                    dmxData[mid_config_dmx] = 0
            if event.code == 11:
                if event.value == 120:  # Scroll up
                    scroll_value += 5
                    if scroll_value > 127:
                        scroll_value = 127
                    if config_mode:
                        scroll_config_value = scroll_value
                    msg = mido.Message('control_change', value=scroll_value, channel=slider_channel)
                    outport.send(msg)
                    dmxData[scroll_dmx] = int(scroll_value / 127 * 255)
                    dmxData[config_value_dmx] = int(scroll_config_value / 127 * 255)
                if event.value == -120:  # Scroll down
                    scroll_value -= 5
                    if scroll_value < 0:
                        scroll_value = 0
                    if config_mode:
                        scroll_config_value = scroll_value
                    msg = mido.Message('control_change', value=scroll_value, channel=slider_channel)
                    outport.send(msg)
                    dmxData[scroll_dmx] = int(scroll_value / 127 * 255)
                    dmxData[config_value_dmx] = int(scroll_config_value / 127 * 255)
            if dmxData[left_dmx] == 255 and dmxData[mid_dmx] == 255 and dmxData[right_dmx] == 255:  # toggle config mode (adjust max scroll value)
                if loop > config_mode_changed_at_loop + 50:  # at least some frames in between
                    if config_mode:
                            config_mode = False
                            print("Leaving config mode (all buttons pressed), max. scrolling value set to {}".format(scroll_config_value))
                    else:
                        config_mode = True
                        print("Entering config mode (all buttons pressed), please select max. scrolling value")
                    config_mode_changed_at_loop = loop
            
            if artNetSocket:
                sendArtNetPacket( ARTNET_UNIVERSE, dmxData, artNetSocket )

            loop += 1

    except Exception as e:
        print(e)
        print("Retrying (consider using sudo or cancel with CTRL+C)...")
    time.sleep(1)