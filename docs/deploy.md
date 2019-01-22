# Deploy

## Install

### Raspberry Pi

1. Prepare the SD card
    1. Download the last version of [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) Lite
    2. Unzip it
    3. Format a SD card of at least 16G with `gnome-disks` (in Ext4)
    4. [Write the OS](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md) on the card
2. Initialize the RPi
    1. Plug the SD card, a screen and a keyboard to the RPi
    2. Start the RPi (make sure to have enough power)
    3. Write down the IP address that is printed on the screen
    4. `sudo raspi-config`
    5. In `raspi-config`, configure these parameters:
        * Network Options
            * Hostname: "rpi_atelier"
            * Network interface names: disable predictable names
        * Localisation Options
            * Change Timezone
            * Change [Keyboard Layout](http://www.soft-alternative.com/raspberry-pi-configurer-clavier-francais-raspbian.php)
            * Change Wi-fi country
        * Interfacing Options
            * SSH: enable
    6. Reboot the RPi
3. Configure the network
    1. Connect the RPi to the computer through Ethernet
    2. Make sure you are on the same network as displayed in 2.3
    3. Send setup files to the RPi: `scp -r deploy pi@<ip>:/home/pi`
    4. Setup network: `ssh pi@<ip> 'cd /home/pi/deploy; ./setup.sh'`
    5. Set [WiFi password](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md) in `/etc/wpa_supplicant/wpa_supplicant.conf` with `wpa_passphrase`
    6. Reboot the RPi
    7. Set your IP to communicate with the RPi: `make config_ip`
    8. `make check_network`
4. [Mount a disk](https://www.raspberrypi-spy.co.uk/2014/05/how-to-mount-a-usb-flash-disk-on-the-raspberry-pi/) for database backup
5. Install the project (Internet access needed):
    * On your machine (not on the RPi): `make download`
    * On your machine (not on the RPi): `make install`
6. Reboot the RPi to start the web server: `make reboot`

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

* `make update`
* If everything went well (e.g. no merge conflicts): `make reboot`
