#!/bin/bash

# IP config
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.bak
sudo cp dhcpcd.conf /etc/dhcpcd.conf

# WiFi networks to connect to
sudo cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf.bak
sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

# Allow both Ethernet and WiFi to run simultaneously
action_wpa="/etc/wpa_supplicant/action_wpa.sh"
sudo cp $action_wpa "$action_wpa.bak"
# Use sudo to keep same permissions
echo -e 'exit 0\n' | sudo cat - $action_wpa > temp
sudo chmod 0755 temp
sudo mv temp $action_wpa

echo "------------"
echo "* Add passwords to /etc/wpa_supplicant/wpa_supplicant.conf with wpa_passphrase"
echo "* Reboot"
echo "------------"
