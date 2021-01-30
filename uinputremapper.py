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
parser.add_argument('-c', '--config', dest="config", help="Path to config file")
parser.add_argument('-v', '--verbose', dest="logging", action="store_true", help="Increase logging")
parser.add_argument('-n', '--numberpad', dest="numberpad", action="store", help="Embed number pad. Provide comma separated list of keycodes to activate/decativate")
parser.add_argument('-t', '--toggle', dest="toggle", action="store", help="Toggle remap on/off. Provide comma separated list of keycodes to activate/decativate")
#29,56,102 mould be LEFTCTRL,LEFTALT,LEFTSHIFT+HOME
#TODO
# parser.add_argument('--raw_config', dest="raw_config", help="TODO raw file with just ints")

args = parser.parse_args()

if args.config:
    try:
        f = open(args.config, 'r')
        data = json.loads(f.read())
        args.logging = data.get('logging')
        args.layout = data.get('layout')
        args.grab_name = data.get('grab_name')
        args.dev_name = data.get('dev_name')
        args.numberpad = data.get('numberpad')
        args.toggle = data.get('toggle')
    except:
        sys.exit("Error loading config files")



if args.logging: print(args)
if args.numberpad:
    if type(args.numberpad)==list:
        numpad_toggle =  args.numberpad
    else:
        numpad_toggle = [int(key) for key in args.numberpad.split(",")]
    if args.logging:
        print(numpad_toggle, "bound to number pad toggle")

if args.list_devices:
    for device in get_devices():
        print(device.path, device.name, device.phys)

if args.grab_name:
    proper_name = args.grab_name
else:
    sys.exit("Grab name not provided")


def get_devices():
    return [evdev.InputDevice(path) for path in evdev.list_devices()]

def grab_device(devices, descriptor):
    #determine if descriptor is a path or a name
    return_device = None
    if len(descriptor) <= 2: #assume that people don't have more than 99 input devices
        descriptor = "/dev/input/event"+descriptor
    if "/dev/" in descriptor: #assume function was passed a path
        for device in devices:
            if descriptor==device.path:
                device.close()
                return_device = evdev.InputDevice(device.path)
            else:
                device.close()
    else: #assume that function was passed a plain text name
        for device in devices:
            if descriptor==device.name:
                device.close()
                return_device = evdev.InputDevice(device.path)
            else:
                device.close()

    return return_device

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
    e.KEY_N: e.KEY_K,
    #colemak has backspace as left shift and right alt as alt_gr
    e.KEY_LEFTSHIFT: e.KEY_BACKSPACE, e.KEY_RIGHTALT: 84
}

qwerty_to_workman_map = {
    
}

#TODO add some way to toggle an "internal numberpad" like found on some laptops
qwerty_internal_numberpad = {
# created based on layout shown here https://www.dummies.com/computers/pcs/how-to-use-the-numeric-keypad-on-your-laptop/
    e.KEY_M: e.KEY_KP0,
    e.KEY_J: e.KEY_KP1,
    e.KEY_K: e.KEY_KP2,
    e.KEY_L: e.KEY_KP3,
    e.KEY_U: e.KEY_KP4,
    e.KEY_I: e.KEY_KP5,
    e.KEY_O: e.KEY_KP6,
    e.KEY_7: e.KEY_KP7,
    e.KEY_8: e.KEY_KP8,
    e.KEY_9: e.KEY_KP9,
    e.KEY_0: e.KEY_KPSLASH,
    e.KEY_P: e.KEY_KPASTERISK,
    e.KEY_SEMICOLON: e.KEY_KPMINUS,
    e.KEY_SLASH: e.KEY_KPPLUS,
    # e.KEY_: e.KEY_KPENTER,
    e.KEY_COMMA: e.KEY_KPCOMMA,
    e.KEY_DOT: e.KEY_KPDOT,
}

dvorak_internal_numberpad = {
    e.KEY_M: e.KEY_KP0,
    e.KEY_H: e.KEY_KP1,
    e.KEY_T: e.KEY_KP2,
    e.KEY_N: e.KEY_KP3,
    e.KEY_G: e.KEY_KP4,
    e.KEY_C: e.KEY_KP5,
    e.KEY_R: e.KEY_KP6,
    e.KEY_7: e.KEY_KP7,
    e.KEY_8: e.KEY_KP8,
    e.KEY_9: e.KEY_KP9,
    e.KEY_0: e.KEY_KPSLASH,
    e.KEY_L: e.KEY_KPASTERISK,
    e.KEY_S: e.KEY_KPMINUS,
    e.KEY_Z: e.KEY_KPPLUS,
    # e.KEY_: e.KEY_KPENTER,
    e.KEY_W: e.KEY_KPCOMMA,
    e.KEY_V: e.KEY_KPDOT,
}

if args.layout=="dvorak":
    default_map = qwerty_to_dvorak_map
    numberpad_map = qwerty_internal_numberpad
elif args.layout=="numberpad":
    default_map = {}
    numberpad_map = qwerty_internal_numberpad
elif args.layout=="colemak":
    default_map = qwerty_to_colemak_map
elif args.layout=="workman":
    default_map = qwerty_to_workman_map
else:
    #TODO add option here to check if a RAW config file has been provided
    sys.exit("No layout provided exiting")

ui = evdev.UInput(name=args.dev_name)

def check_held(held_keys, key_list):
    all_held = True
    for key in key_list:
        if key not in held_keys:
            all_held=False
            break
    return all_held

def event_loop(keybeeb):
    keybeeb_name = keybeeb.name
    try:
        held_keys = []
        numberpad = False
        toggle = False
        numberpad_time = time.time()
        toggle_time = time.time()
        for ev in keybeeb.read_loop():
            outcode = ev.code #key not found in map send unmodified keycode
            if ev.value == 1: #modifier pressed down
                held_keys.append(ev.code)
            elif ev.value == 0: #modifier released!
                if ev.code in held_keys:
                    held_keys.remove(ev.code)
            if args.numberpad:
                # print(held_keys)
                if check_held(held_keys, numpad_toggle) and (time.time()-numberpad_time)>=2:
                    numberpad_time = time.time()
                    ui.write(e.EV_KEY, e.KEY_NUMLOCK, 1)
                    ui.write(e.EV_KEY, e.KEY_NUMLOCK, 0)
                    numberpad = not numberpad
                    print("Toggle numpad:", numberpad)
            if args.toggle:
                if check_held(held_keys, args.toggle) and (time.time()-toggle_time)>=2:
                    toggle_time = time.time()
                    toggle = not toggle
                    print("Toggle layout:", toggle)




            if not toggle and ev.code in default_map: #default no modifiers held
                if ev.code in default_map:
                    outcode = default_map[ev.code]
            if numberpad and ev.code in numberpad_map:
                outcode = numberpad_map[ev.code]

            ui.write(ev.type, outcode, ev.value)
            if args.logging: print(ev)
    except OSError:
        print("device disconnected!")



time.sleep(1)
keybeeb = grab_device(get_devices(), proper_name)

if keybeeb is None:
    sys.exit("Improperly selected device")

while True:
    devices = get_devices()
    keybeeb = grab_device(devices, proper_name)
    if keybeeb is not None:
        print("GRABBING FOR REMAPPING: "+str(keybeeb))
        keybeeb.grab()
        event_loop(keybeeb)
    print("Device probably was disconnected")
    time.sleep(5)