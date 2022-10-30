#!/bin/bash
#Purpose: Remove Project Fairy
#_START_#

echo "This script is going to remove MySQL and UFW services after 3 seconds"
echo "Please hit [ENTER] key to continue"
read _

sudo systemctl stop mysql.service
sleep 5
sudo apt-get remove --purge mysql* -y
sudo apt-get remove dbconfig-mysql -y

sudo systemctl stop ufw
sleep 5
sudo apt-get remove ufw -y
sudo apt-get purge ufw -y

sudo systemctl stop nginx
sleep 5
sudo apt-get remove nginx -y
sudo apt-get purge nginx -y

sudo systemctl stop supervisor
sleep 5
sudo apt-get remove supervisor -y
sudo apt-get purge supervisor -y

sudo rm -rf /etc/mysql /var/lib/mysql /var/lib/mysql-keyring /var/lib/mysql-files /etc/config.json /etc/nginx etc/supervisor/conf.d/flask.conf /var/log/flask

sudo apt-get remove python3-venv -y
sudo apt-get purge python3-venv -y

sudo apt-get remove python3-pip -y
sudo apt-get purge python3-pip -y

sudo rm -rf ~/ProjectFairy

sudo apt-get autoremove -y
sudo apt-get autoclean -y

unset FLASKY_ADMIN PUBLIC_IP_ADDRESS PROJECT_FOLDER MAIL_USERNAME SQLALCHEMY_DATABASE_URI SECRET_KEY SECRET_KEY_FOR_TOKEN MAIL_PASSWORD FLASKY_MAIL_SENDER MYSQL_USER_NAME MYSQL_USER_PASSWORD MYSQL_ROOT_PASSWORD

echo "Project Fairy has been removed successfully!"

#_END_#