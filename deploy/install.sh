#!/bin/sh

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y sqlite3 build-essential libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev zlib1g libsqlite3-dev python3 python3-pip vim

curl https://pyenv.run | bash
echo >> ~/.bashrc
echo 'export PATH="/home/pi/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
exec $SHELL

pyenv install 3.9.1
cd ../atelier
pyenv local 3.9.1
cd ../deploy

curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
exec $SHELL

# Install Pipenv
sudo pip3 install --upgrade pip
sudo pip3 install pipenv
pipenv install

git config --global user.email "you@example.com"
git config --global user.name "Vincent Lefoulon"

python3 config.py ../atelier/config.json

# Run web server at startup
crontab -r
(crontab -l 2>/dev/null; echo "@reboot cd /home/pi/atelier && PATH="'"$PATH:/usr/local/bin"'" && make prod") | crontab -

echo "------------"
echo "Installation finished."
echo "Please reboot to start the server."
echo "------------"
