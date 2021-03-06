# Production

## Install

### Raspberry Pi

1. [Prepare the SD card](https://www.framboise314.fr/preparez-votre-carte-sd-raspbian-sur-le-raspberry-pi/)
2. Initialize the RPi
    1. Plug the SD card, a screen and a keyboard to the RPi
    2. Start the RPi (make sure to have enough power)
    3. Login with the default user: `pi` / `raspberry`
    4. `sudo raspi-config`
    5. In `raspi-config`, configure these parameters:
        * Localisation Options
            * Change leyboard layout
            * Change timezone
            * Change Wi-fi country
        * System Options
            * Hostname: `rpi-atelier`
        * Advanced Options
            * Network interface names: `predictable names disabled`
        * Interfacing Options
            * SSH: `enable`
    6. Install French locale
        * Uncomment `fr_FR.UTF-8` in `/etc/locale.gen`
        * `sudo locale-gen`
        * Make sure `fr_FR.UTF-8` is installed: `locale -a`
    7. Reboot the RPi: `sudo reboot`
3. Configure the network (needs the screen and the keyboard on the RPi)
    1. Connect the RPi to the computer through Ethernet
    2. Find its IP: `ifconfig` then look at `eth0` interface
    3. Make sure your computer's Ethernet interface is on the same network as the RPi
        * Set your computer's Ethernet interface IPv4 address
        * Use the same mask as the RPi
        * Check: `ping <rpi-ip>`
    4. Send setup files to the RPi: `scp -r deploy pi@<ip>:/home/pi`
    5. Setup network: `ssh pi@<ip> 'cd /home/pi/deploy; ./setup.sh'`
        * The Ethernet IP is statically set to the one defined in `dhcpcd.conf`
        * WiFi networks to connect to automatically are defined in `wpa_supplicant.conf`
        * We configure WPA to allow Ethernet and WiFi to be used simultaneously
    6. Set [WiFi password](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md) in `/etc/wpa_supplicant/wpa_supplicant.conf` with `wpa_passphrase <ssid> >> /etc/wpa_supplicant/wpa_supplicant.conf`. The SSIDs are already setup but others can be found with `sudo iwlist wlan0 scan`.
    7. Reboot the RPi
    8. Set your IP to communicate with the RPi: `make config_ip`
    9. `make check_network`
4. [Mount a disk](https://www.raspberrypi-spy.co.uk/2014/05/how-to-mount-a-usb-flash-disk-on-the-raspberry-pi/) for database backup
5. Install the project (Internet access needed):
    * On your machine (not on the RPi): `make download` will `git clone` the repo
    * On your machine (not on the RPi): `make install` will install the dependencies (/!\ requires **human input**)
    * Configure the project in `atelier/config.json`:
        * `http_credentials` (required)
        * `sms_credentials` (optional)
        * `db_backup_paths` (optional)
6. Reboot the RPi to start the web server: `make reboot`
7. Open `http://<rpi-ip>:5000/debug` and observe the CPU usage. If it's low, you can [reduce the frequency](http://with-raspberrypi.blogspot.com/2014/03/cpu-frequency.html).

### Controllino

* Install [Webduino](https://github.com/sirleech/Webduino) library
* Install [Controllino board manager](https://github.com/CONTROLLINO-PLC/CONTROLLINO_Library#installation-guide)
* Select board `Controllino MAXI automation`

## Update

### Controllino

On your machine:

* `make edit_ino`
* Write the program onto the Controllino

### Raspberry Pi

On your machine:

First, update the Python package versions in the `poetry.lock`:

```
poetry update
```

Commit and push.

Then:

* `make update`
* If everything went well (e.g. no merge conflicts): `make reboot`
