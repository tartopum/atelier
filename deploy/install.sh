#!/bin/bash

set -eu

sudo apt-get update --allow-releaseinfo-change
sudo apt-get -y upgrade
sudo apt-get install -y sqlite3 build-essential libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev zlib1g libsqlite3-dev python3 python3-pip vim

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10

echo
echo "Installing pyenv..."
curl https://pyenv.run | bash
echo >> ~/.profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init -)"' >> ~/.profile
echo >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

echo
echo "Installing Python 3.11..."
pyenv install 3.11

echo
echo "Installing poetry..."
curl -sSL https://install.python-poetry.org | python3 -
echo >> ~/.profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile
echo >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
# We need to run the commands since bashrc is for interactive envs and cannot
# be sourced
export PATH="$HOME/.local/bin:$PATH"

echo
echo "Installing Python dependencies..."
cd ../atelier
poetry install --no-dev

cp config.json.template config.json

# Run web server at startup
echo
echo "Creating a cron to start server at boot..."
(crontab -l 2>/dev/null; echo "@reboot export PATH="$HOME/.pyenv/bin:$HOME/.pyenv/shims:$HOME/.local/bin:$PATH" && cd /home/pi/atelier && make prod > last.log") | crontab -
