#!/bin/sh

sudo apt-get update
sudo apt-get -y upgrade
sudo pip3.7 install --upgrade pip pipenv

git stash
git pull
git stash apply
STASH_RET=$?
pipenv install

echo "------------"
if [ "$STASH_RET" -eq "0" ]; then
    echo "Update finished."
    echo "Please reboot to restart the server."
else
    echo "CONFLICTS DETECTED."
    echo "Please solve them and add the changes to the git index."
    echo "Then reboot to restart the server."
fi
echo "------------"
