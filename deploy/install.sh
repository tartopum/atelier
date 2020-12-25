#!/bin/bash

set -eu

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y sqlite3 build-essential libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev zlib1g libsqlite3-dev python3 python3-pip vim

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10

echo
echo "Installing poetry..."
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
echo >> ~/.bashrc
echo 'export PATH="$HOME/.poetry/bin:$PATH"' >> ~/.bashrc
# We need to run the commands since bashrc is for interactive envs and cannot
# be sourced
export PATH="$HOME/.poetry/bin:$PATH"

git config --global user.email "vincent.lefoulon@free.fr"
git config --global user.name "Vincent Lefoulon"

python3 config.py ../atelier/config.json

cd ../atelier
poetry install

# Run web server at startup
crontab -r
(crontab -l 2>/dev/null; echo "@reboot cd /home/pi/atelier && PATH="'"$HOME/.poetry/bin:$HOME/.pyenv/bin:$PATH:/usr/local/bin"'" && make prod") | crontab -

echo "------------"
echo "Installation finished."
echo "Please reboot to start the server."
echo "------------"
