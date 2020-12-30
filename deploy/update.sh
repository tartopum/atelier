#!/bin/bash

set -eu

echo
echo "Updating Debian packages..."
sudo apt-get update
sudo apt-get -y upgrade

echo
echo "Pulling git repo..."
git pull

echo
echo "Updating Python dependencies..."
export PATH="$HOME/.poetry/bin:$PATH"
poetry install --no-dev

echo
echo "Update finished."
echo "Please reboot to restart the server."
