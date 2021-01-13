import os
import sys
import time
import argparse
import json

import evdev
from evdev import ecodes as e

# from keyboard_map import default_map, shift_map, ctrl_map
#requies either sudo when run or for the running user to be in the `input` user group

#TODO add test to determine if user is in the right input group

parser = argparse.ArgumentParser(description="""Remap keyboard to other common layouts. Highly extensible!
Grabbing means that all of the keystrokes sent from the selected keyboard will be swallowed before propigating to userspace.
The idea is that you can use one of the provided layouts (or your own!) and remap a Qwerty (or others depending on community support) 
keyboard to your preferred layout, in a way that works universally, in X11, wayland or even TTY terminals!""")
#TODO add something to define what users base layout is?
parser.add_argument('-l', '--layout', dest="layout", help="Common name of layout to switch to [dvorak|colemak] currently supported")
parser.add_argument('--grab_name', dest="grab_name", help="Exact Name of keyboard to grab")
parser.add_argument('--dev_name', default="Remapped Keyboard", dest='dev_name', help="Name to use for the newly created uinput device")
parser.add_argument('-ls', '--list', action="store_true", dest="list_devices", help="List attached available devices")
parser.add_argument('-c', '--config', dest="config_dest", help="Path to config file")
parser.add_argument('-v', '--verbose', dest="logging", action="store_true", help="Increase logging")
#TODO
# parser.add_argument('--raw_config', dest="raw_config", help="TODO raw file with just ints")

args = parser.parse_args()
print(args)

def get_devices():
    return [evdev.InputDevice(path) for path in evdev.list_devices()]

devices = get_devices()

i=0
for device in devices:
    i+=1
    if args.list_devices: print(device.path, device.name, device.phys)

if args.list_devices: sys.exit()
if args.grab_name:
    proper_name = args.grab_name
else:
    sys.exit("Grab name not provided")

def load_config(path):
    try:
        f = open(path, 'r')
        data = json.loads(f.read())
        return eval("".join(data['default_map']))
    except:
        sys.exit("Error loading config files")

qwerty_to_dvorak_map = {
#top row is similar for dvorak
    e.KEY_MINUS: e.KEY_LEFTBRACE, e.KEY_EQUAL:e.KEY_RIGHTBRACE,
    e.KEY_Q: e.KEY_APOSTROPHE, e.KEY_W: e.KEY_COMMA, e.KEY_E: e.KEY_DOT, e.KEY_R:e.KEY_P, e.KEY_T:e.KEY_Y, e.KEY_Y: e.KEY_F, e.KEY_U:e.KEY_G, e.KEY_I:e.KEY_C, e.KEY_O:e.KEY_R, e.KEY_P:e.KEY_L, e.KEY_LEFTBRACE:e.KEY_SLASH, e.KEY_RIGHTBRACE:e.KEY_EQUAL,
    e.KEY_A:e.KEY_A, e.KEY_S:e.KEY_O, e.KEY_D:e.KEY_E, e.KEY_F:e.KEY_U, e.KEY_G:e.KEY_I, e.KEY_H:e.KEY_D, e.KEY_J:e.KEY_H, e.KEY_K:e.KEY_T, e.KEY_L:e.KEY_N, e.KEY_SEMICOLON:e.KEY_S, e.KEY_APOSTROPHE:e.KEY_MINUS,
    e.KEY_Z:e.KEY_SEMICOLON, e.KEY_X:e.KEY_Q, e.KEY_C:e.KEY_J, e.KEY_V:e.KEY_K, e.KEY_B:e.KEY_X, e.KEY_N:e.KEY_B, e.KEY_M:e.KEY_M, e.KEY_COMMA:e.KEY_W, e.KEY_DOT:e.KEY_V, e.KEY_SLASH:e.KEY_Z
}

qwerty_to_colemak_map = {
    e.KEY_E: e.KEY_F, e.KEY_R: e.KEY_P, e.KEY_T: e.KEY_G, e.KEY_Y: e.KEY_J, e.KEY_U: e.KEY_L, e.KEY_I: e.KEY_U, e.KEY_O: e.KEY_Y, e.KEY_P: e.KEY_SEMICOLON,
    e.KEY_S: e.KEY_R, e.KEY_D: e.KEY_S, e.KEY_F: e.KEY_T, e.KEY_G: e.KEY_D, e.KEY_H: e.KEY_H, e.KEY_J: e.KEY_N, e.KEY_K: e.KEY_E, e.KEY_L:e.KEY_I, e.KEY_SEMICOLON: e.KEY_O,
    e.KEY_N: e.KEY_K
}

qwerty_to_workman_map = {
    
}

#TODO add some way to toggle an "internal numberpad" like found on some laptops
qwerty_internal_numberpad = {
    
}

if args.layout=="dvorak":
    default_map = qwerty_to_dvorak_map
elif args.layout=="colemak":
    default_map = qwerty_to_colemak_map
elif args.layout=="workman":
    default_map = qwerty_to_workman_map
else:
    #add option here to check if a RAW config file has been provided
    sys.exit("No layout provided exiting")

#past here will probably end up grabbing a keyboard for remapping

ui = evdev.UInput(name=args.dev_name)

def grab_dev(name):
    keybeeb = None
    for device in devices:
        if proper_name==device.name:
            device.close()
            keybeeb = evdev.InputDevice(device.path)
        else:
            device.close()

    return keybeeb


def event_loop(keybeeb):
    held_modifiers = [e.KEY_LEFTSHIFT, e.KEY_RIGHTSHIFT]
    toggle_modifiers = [e.KEY_SCROLLLOCK, e.KEY_CAPSLOCK]
    keybeeb_name = keybeeb.name
    try:
        modifiers = []
        for event in keybeeb.read_loop():
            ev_type = event.type
            ev_code = event.code
            ev_value = event.value
            #held modifier processing
            if ev_code in held_modifiers:
                if ev_value == 1: #pressed down
                    modifiers.append(ev_code)
                elif ev_value == 0: # released
                    if ev_code in modifiers: #chec
                        modifiers.remove(ev_code)
            if ev_code in toggle_modifiers:
                if ev_value == 1:
                    modifiers.append(ev_code)
                elif ev_value == 0:
                    if ev_code in modifiers:
                        modifiers.remove(ev_code)
            # TODO add support for "remapping" keys when modified (to be used for maintaining muscle memory for shortcuts)
            # print(modifiers)[]
            # if (e.KEY_LEFTSHIFT in modifiers or e.KEY_RIGHTSHIFT in modifiers): #if shift button is being held
            #     if ev_code in shift_map:
            #         outcode = shift_map[ev_code]
            # elif (e.KEY_RIGHTCTRL in modifiers or e.KEY_LEFTCTRL in modifiers):
            #     if ev_code in ctrl_map:
            #         outcode = ctrl_map[ev_code]
            if ev_code in default_map: #default no modifiers held
                if ev_code in default_map:
                    outcode = default_map[ev_code]
            else:
                outcode = ev_code
            ui.write(ev_type, outcode, ev_value)
            if args.logging: print(event)
    except OSError:
    # ui.close()
        print("device disconnected!")
        # event_loop(grab_dev(keybeeb_name))



time.sleep(1)
keybeeb = grab_dev(proper_name)

if keybeeb is None:
    sys.exit("Improperly selected device")

while True:
    devices = get_devices()
    keybeeb = grab_dev(proper_name)
    if keybeeb is not None:
        print("GRABBING FOR REMAPPING: "+str(keybeeb))
        keybeeb.grab()
        event_loop(keybeeb)
    print("Device probably was disconnected")
    time.sleep(5)
# event_loop(keybeeb)

#handle OS ERROR somewhere