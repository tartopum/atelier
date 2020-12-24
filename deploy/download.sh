#!/bin/bash

sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y git

git clone https://github.com/tartopum/atelier ../atelier
