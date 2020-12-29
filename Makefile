RPI_USER=pi
RPI_IP_ETH=192.168.167.101
RPI_IP_WIFI=192.168.168.78
RPI_SSH_PORT=22
ETH_INT=enp3s0 # The network interface to connect to the RPi
RPI_HOME=/home/${RPI_USER}
SSH_HOST_LOCAL=${RPI_USER}@${RPI_IP_ETH}
SSH_HOST=${RPI_USER}@${RPI_IP_WIFI}
SSH_ARGS=-p ${RPI_SSH_PORT} ${SSH_HOST}


.PHONY: dev
dev:
	-cat pid | xargs kill
	poetry run python run_server.py --debug

.PHONY: fake_arduino
fake_arduino:
	poetry run python fake_arduino/server.py

.PHONY: prod
prod:
	-cat pid | xargs kill
	poetry run python run_server.py & echo "$$!" > pid

.PHONY: edit_ino
edit_ino:
	arduino arduino/arduino.ino &

.PHONY: ssh_local
ssh_local:
	ssh ${SSH_HOST_LOCAL}

.PHONY: ssh
ssh:
	ssh ${SSH_ARGS}

.PHONY: check_network
check_network:
	ssh ${SSH_HOST_LOCAL} 'hostname -I; /sbin/iwgetid; ping -c 3 www.google.com'

# Customize ${ETH_INT} before
.PHONY: config_ip
config_ip:
	sudo ifconfig ${ETH_INT} 192.168.167.102 netmask 255.255.255.0

.PHONY: download
download:
	ssh ${SSH_ARGS} 'cd ${RPI_HOME}/deploy; ./download.sh'

.PHONY: install
install:
	ssh ${SSH_ARGS} 'cd ${RPI_HOME}/atelier/deploy; ./install.sh'

.PHONY: credentials
credentials:
	ssh ${SSH_ARGS} 'cd ${RPI_HOME}/atelier/deploy; python3 credentials.py'
	
.PHONY: update
update:
	ssh ${SSH_ARGS} 'cd ${RPI_HOME}/atelier/deploy; ./update.sh'

.PHONY: shutdown
shutdown:
	ssh ${SSH_ARGS} 'sudo shutdown -h now'

.PHONY: reboot
reboot:
	ssh ${SSH_ARGS} 'sudo reboot'

.PHONY: download_db
download_db:
	scp -P ${RPI_SSH_PORT} ${SSH_HOST}:${RPI_HOME}/atelier/db.sqlite3 rpi_db.sqlite3

.PHONY: upload_db
upload_db:
	@echo "Copying rpi_db.sqlite3 to uploaded_db.sqlite3 on the RPi..."
	@echo
	scp -P ${RPI_SSH_PORT} rpi_db.sqlite3 ${SSH_HOST}:${RPI_HOME}/atelier/uploaded_db.sqlite3
