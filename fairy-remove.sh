#!/bin/bash
#Purpose: Remove Project Fairy
#_START_#
set -x

echo "This script is going to remove Project Fairy and all related services"
echo "Please hit [ENTER] key to continue"
read _

sudo systemctl stop mysql.service
sleep 2
sudo apt-get remove --purge mysql* -y
sudo apt-get remove dbconfig-mysql -y

sudo systemctl stop ufw
sleep 2
sudo apt-get remove ufw -y
sudo apt-get purge ufw -y

sudo systemctl stop nginx
sleep 5
sudo apt-get remove nginx -y
sudo apt-get purge nginx -y

sudo systemctl stop supervisor
sleep 2
sudo apt-get remove supervisor -y
sudo apt-get purge supervisor -y

sudo rm -r /etc/mysql /var/lib/mysql /var/lib/mysql-keyring /var/lib/mysql-files /etc/config.json
sudo rm -r /etc/nginx /var/log/flask /etc/supervisor

sudo apt-get remove python3-venv -y
sudo apt-get purge python3-venv -y

sudo apt-get remove python3-pip -y
sudo apt-get purge python3-pip -y

sudo rm -r ~/ProjectFairy

sudo apt-get autoremove -y
sudo apt-get autoclean -y

unset FLASKY_ADMIN PUBLIC_IP_ADDRESS PROJECT_FOLDER MAIL_USERNAME SQLALCHEMY_DATABASE_URI SECRET_KEY SECRET_KEY_FOR_TOKEN MAIL_PASSWORD FLASKY_MAIL_SENDER MYSQL_USER_NAME MYSQL_USER_PASSWORD MYSQL_ROOT_PASSWORD

sudo rm -rf ~/fairy-install.sh ~/fairy-remove.sh

echo "Project Fairy has been removed successfully!"

#_END_#