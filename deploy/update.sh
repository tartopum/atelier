#!/bin/sh

sudo apt-get update
sudo apt-get -y upgrade
sudo pip3.7 install --upgrade pip pipenv

cd ../atelier
git pull
sudo reboot
