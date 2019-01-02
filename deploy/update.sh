#!/bin/sh

sudo apt-get update
sudo apt-get -y upgrade
sudo pip3.7 install --upgrade pip pipenv

git stash
git pull
git stash apply
pipenv install

echo "------------"
echo "Update finished."
echo "Please reboot to restart the server."
echo "------------"
