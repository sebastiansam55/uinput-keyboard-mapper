# uinput-keyboard-mapper
UInput Level Keyboard remapper for linux, written in python.

The program either has to be run as root or you have to add the user running the program to the `input` user group (for ubuntu). If you are having issues with this look at the python-evdev documentation for how to add the user to the right group.

## Usage

`python3 uinputremapper.py --grab_name "<keyboard name>" -l dvorak`

Will try to grab the keyboard with the specified name and remap it from an assumed qwerty layout to dvorak layout. Only dvorak and colemak (no alt-gr support!) are currently supported. 

You can use `--dev_name` if you wish to control what the new keyboard device will be called. 

In order to determine what the name of your keyboard is you can run `python3 uinputremapper.py -ls` which will print out a list of the uinput device names found on the computer.

Abbreviated Output:

```bash
/dev/input/event24 Remapped Keyboard py-evdev-uinput
/dev/input/event9 Keychron K8 Keychron K8 usb-0000:00:14.0-1.3/input1
/dev/input/event6 Keychron K8 Keychron K8 usb-0000:00:14.0-1.3/input0
/dev/input/event5 Logitech USB Optical Mouse usb-0000:00:14.0-1.2/input0
```

The Keychron K8 shows up twice, one is for the regular keyboard and one is for the function keys and one is for the regular keyboard. The exact device name of the Keychron K8 is everything between the end of the `/dev/input` path and the start of the BUSID, in this case it would be "Keychron K8 Keychron K8"

The list printed by `uinputremapper.py`  is the same order the program will decide which device to grab based on name match, and it will use the first match that it finds so if the media control version shows above the regular keyboard name and they both have identical device names you will run into issues. 

If this device name issue causes you any issues open an issue and I'll get around to fixing it. The program also accepts the path to the device or even the number of the device as an option. Note that the device number can and will change. 

## Config File
The program can accept a json file with in the following type of format;
```json
{
    "logging": false,
    "layout": "numberpad",
    "grab_name": "AT Translated Set 2 keyboard",
    "dev_name": "Dvorak Keyboard",
    "numberpad": [29,56,102],
    "toggle": [29,56,107]
}
```
The options are directly related to the flags used by `uinputremapper.py`. With this particular config it will enable an "embedded" number pad when you press the key combination as described in the `numberpad option`. With the rest of the keys operating as expected for qwerty layout. 

The list of numbers provided in `numberpad` can be found with `evtest`, `xev` or by running this program with the `-v` flag.

Toggle operates in a similar way, turning the map on or off. In the example config above pressing `LeftCtrl+LeftShift+End` will switch the keyboard from dvorak back to qwerty.

Both of the toggle option have a cooldown of 2 seconds as otherwise they will fire a number of times even when the keys are held for only a couple of seconds.

## Requirements

In addition to making sure that your user is either in the `input` group you also have to have the following python modules installed:

* `evdev` - `pip3 install evdev`

  The rest of the modules used should be installed in a basic python installation

## WHY???

There are other easier and more reliable ways to remap your qwerty keyboard to whatever layout you desire but from what I googled before working on this most relied on using some part of the X11 system which means that the remap wont work if you use wayland or in the TTY thing (CTRL+ALT+1). So i threw this together over a few weeks to the point it was semi usable and slapped it on github in case anyone else was looking for a universal solution like I was.

## Contributions

If something is missing from the program that you would like feel free to open a PR or to open an issue outlining what the program is missing. Provide logs (USE `-v`) if something is not working please!

## Notes

Some devices have a number of different devices associated with them you need to determine which is the "main" keyboard device.

Additionally some devices (like my Keychron K8) have different `uinput` names depending on how it is connected to the computer; the examples shown above are of using the keyboard with a wired connection. When connected via bluetooth the main keyboard portion device shows up as "Keychron K8 Keyboard" and the media/other functions device shows up as "Keychron K8 System Control"

The program should survive and try to regrab the device every 5 seconds if the device is disconnected or interrupted in some way (sleeping/disconnect).

I use only the dvorak so I don't guarantee the other layouts are correct at all. ALT-GR is weird. Doesn't seem like there is a specific scan code that `evdev` has that is related to it. 

### Startup?

On my computer I have it setup to launch via cron at startup. (`sudo crontab -e`);

`@reboot /path/to/shellscript/with/options`

Where my script (which is executable) looks like this;
```bash
python3 /path/uinput-keyboard-mapper/uinputremapper.py --grab_name "Keychron K8 Keychron K8" -l dvorak
```



## Security

There are considerations to be made about adding the user to the input group or about running the program as root, feel free to make them.

## TODO
Add alternate fallback device name flag that is only captured when the primary is not found.

Map for common keys to `evdev` keycodes. Using the int values is not the ideal solution but is the fastest one.