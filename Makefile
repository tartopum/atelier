RPI_USER=pi
RPI_IP_ETH=192.168.167.101
RPI_IP_WIFI=192.168.168.77
RPI_SSH_PORT=5022
ETH_INT=enp3s0 # The network interface to connect to the RPi
RPI_HOME=/home/${RPI_USER}
SSH_HOST_LOCAL=${RPI_USER}@${RPI_IP_ETH}
SSH_HOST=-p ${RPI_SSH_PORT} ${RPI_USER}@${RPI_IP_WIFI}


.PHONY: dev_fake
dev_fake:
	pipenv run python server.py --aip 127.0.0.1 --aport 5001 --debug

.PHONY: dev
dev:
	pipenv run python server.py --debug

.PHONY: fake_arduino
fake_arduino:
	pipenv run python fake_arduino/server.py

.PHONY: prod
prod:
	-cat pid | xargs kill
	rm -f server.log server.err
	pipenv run python server.py > server.log 2> server.err & echo "$$!" > pid

.PHONY: edit_ino
edit_ino:
	arduino arduino/arduino.ino &

.PHONY: ssh_local
ssh_local:
	ssh ${SSH_HOST_LOCAL}

.PHONY: ssh
ssh:
	ssh ${SSH_HOST}

.PHONY: check_network
check_network:
	ssh ${SSH_HOST_LOCAL} 'hostname -I; /sbin/iwgetid; ping -c 3 www.google.com'

# Customize ${ETH_INT} before
.PHONY: config_ip
config_ip:
	sudo ifconfig ${ETH_INT} 192.168.167.102 netmask 255.255.255.0

.PHONY: download
download:
	ssh ${SSH_HOST} 'cd ${RPI_HOME}/deploy; ./download.sh'

.PHONY: install
install:
	ssh ${SSH_HOST} 'cd ${RPI_HOME}/atelier/deploy; ./install.sh'

.PHONY: credentials
credentials:
	ssh ${SSH_HOST} 'cd ${RPI_HOME}/atelier/deploy; python3 credentials.py'
	
.PHONY: update
update:
	ssh ${SSH_HOST} 'cd ${RPI_HOME}/atelier/deploy; ./update.sh'

.PHONY: shutdown
shutdown:
	ssh ${SSH_HOST} 'sudo shutdown -h now'

.PHONY: reboot
reboot:
	ssh ${SSH_HOST} 'sudo reboot'

.PHONY: ping
ping:
	ping ${RPI_IP_WIFI}
