from subprocess import check_output, STDOUT
import mido

MOUSE_NAME="Logitech Wireless Mouse"
MAPPING = {10: "left_mouse_btn_keyboard_1", 11: "right_mouse_btn_keyboard_2", 12:"middle_mouse_btn_keyboard_3"}

mouse_id=-1
xinput_list_command="xinput"
xinput_str = check_output(xinput_list_command, stderr=STDOUT).decode()

xinput_list = xinput_str.split('\n') 
virtual_core_keyboard_section = False
for line in xinput_list:
    if line.__contains__("Virtual core keyboard"):
        virtual_core_keyboard_section = True
    if virtual_core_keyboard_section:  # mouse is remapped as keyboard using /etc/udev/hwdb.d/99-mouse-remap.hwdb
        if line.__contains__(MOUSE_NAME):
            mouse_id=int(line[line.find("id=") + len("id="):line.find("[")])
            break

xinput_query_command = "xinput --query-state " + str(mouse_id) # caution, use key[] instead of button[] below
outport = mido.open_output()
states = dict()
for key in MAPPING:
    states[key] = 0
while True:
    xinput_str = check_output(xinput_query_command, stderr=STDOUT, shell=True).decode()
    state_list = xinput_str.split('\n')
    for line in state_list:
        for key in MAPPING:
            if line.__contains__("key[{}]=down".format(key)):
                if states[key] == 0:  # not yet active
                    states[key] = 1
                    msg = mido.Message('note_on', note=key)
                    outport.send(msg)
                break
            if line.__contains__("key[{}]=up".format(key)):
                if states[key] == 1:  # still active
                    states[key] = 0
                    msg = mido.Message('note_off', note=key)
                    outport.send(msg)
                break
