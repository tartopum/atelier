#!/bin/bash

set -eu

echo
echo "Updating Debian packages..."
sudo apt-get update
sudo apt-get -y upgrade

echo
echo "Pulling git repo..."
git stash
git pull
git stash apply
STASH_RET=$?

echo
echo "Updating Python dependencies..."
export PATH="$HOME/.poetry/bin:$PATH"
poetry install

echo
echo
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
