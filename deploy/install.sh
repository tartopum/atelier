#!/bin/sh

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y build-essential libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev zlib1g

# Install Python 3.7
python3.7 -V
if [ $? -ne 0 ];
then
    PY_DIR="Python-3.7.0"
    if [ ! -d "$PY_DIR" ]; then
        wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
        tar -xzvf Python-3.7.0.tgz
    fi
    cd $PY_DIR
    ./configure
    make
    sudo make install
fi

python3.7 -V
if [ $? -ne 0 ];
then
    exit 1
fi

sudo rm -rf Python-3.7.0*

# Install Pipenv
sudo pip3.7 install --upgrade pip
sudo pip3.7 install pipenv gevent
pipenv install

# Run web server at startup
crontab -r
(crontab -l 2>/dev/null; echo "@reboot cd /home/pi/atelier && make prod") | crontab -

echo "------------"
echo "Installation finished."
echo "Please reboot to start the server."
echo "------------"
