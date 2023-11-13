#!/bin/bash
#Purpose: Install Project Fairy
#_START_#
set -x

#  update and upgrade Ubuntu packages
sudo NEEDRESTART_MODE=a apt update -y && sudo NEEDRESTART_MODE=a  apt upgrade -y

# Generating password for MySQL ROOT user
export MYSQL_ROOT_PASSWORD=`date +%s | sha256sum | base64 | head -c 30`

# Generating username and password for standard user
export MYSQL_USER_NAME="mysql_user"

export MYSQL_USER_PASSWORD=`date +%m | sha256sum | base64 | head -c 30`

# install MySQL package
sudo NEEDRESTART_MODE=a  apt install mysql-server -y

# run MySQL service
sudo systemctl start mysql.service

sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_ROOT_PASSWORD'; \q"

sudo NEEDRESTART_MODE=a  apt install python3 -y && sudo NEEDRESTART_MODE=a  apt install git -y
sudo NEEDRESTART_MODE=a  apt install aptitude -y
sudo NEEDRESTART_MODE=a  aptitude -y install expect


SECURE_MYSQL=$(expect -c "
set timeout 10

spawn mysql_secure_installation

expect \"Please enter root password\"
send \"$MYSQL_ROOT_PASSWORD\r\"

expect \"Would you like to setup VALIDATE PASSWORD component?\"
send \"n\r\"

expect \"Change password for root?\"
send \"n\r\"

expect \"Remove anonymous users?\"
send \"y\r\"

expect \"Disallow root login remotely?\"
send \"y\r\"

expect \"Remove test database and access to it?\"
send \"y\r\"

expect \"Reload privilege tables now?\"
send \"y\r\"

expect eof
")

echo "$SECURE_MYSQL"

# Generating MySQL connection string for  SQLAlchemy
export SQLALCHEMY_DATABASE_URI="mysql://$MYSQL_USER_NAME:$MYSQL_USER_PASSWORD@localhost/fairy_db?charset=utf8"
sudo NEEDRESTART_MODE=a aptitude -y purge expect

#  Generating secrets for Flask App
export SECRET_KEY=`date +%ss | sha256sum | base64 | head -c 30`
export SECRET_KEY_FOR_TOKEN=`date +%mm | sha256sum | base64 | head -c 30`

#  Mail Settings setup
echo "Please add required information for your SMTP server."
read -p "Step 1. Enter email address from that App will send emails to users:  " MAIL_USERNAME
read -p "Step 2. Enter password for above email address for SMTP server:  " MAIL_PASSWORD
read -p "Step 3. Enter email for 'Reply To' field (usually same as email address):  " FLASKY_MAIL_SENDER
echo ""
echo "IMPORTANT! Administrator account setup."
read -p "Enter email address of Fairy Web App Administrator. Email will be used for Login:  " FLASKY_ADMIN

#  Showing credentials yo user:
echo <<EOF
"#############################################################"
"#                                                           #"
"# PLEASE RECORD BELOW CREDENTIALS! 		                     #"
"# MySQL root password: $MYSQL_ROOT_PASSWORD                 #"
"# MySQL user name: $MYSQL_USER_NAME                         #"
"# MySQL user password: $MYSQL_USER_PASSWORD                 #"
"# SECRET_KEY for Flask App: $SECRET_KEY                     #"
"# SECRET_KEY_FOR_TOKEN: $SECRET_KEY_FOR_TOKEN               #"
"#                                                           #"
"#############################################################"
EOF

# Uncomment below code if you want to connect to MySQL BD from any IP
# This option is switched off by default for security reason
echo "[mysqld]" | sudo tee -a /etc/mysql/my.cnf > /dev/null
echo "bind-address = 0.0.0.0" | sudo tee -a /etc/mysql/my.cnf > /dev/null
sudo systemctl restart mysql.service
sleep 5

echo "Creating DB, required tables and admin account"
# Creating new user and assign permissions
mysql -u root -p$MYSQL_ROOT_PASSWORD <<EOF
CREATE USER '$MYSQL_USER_NAME'@'%' IDENTIFIED BY '$MYSQL_USER_PASSWORD';
GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT, REFERENCES, RELOAD on *.* TO '$MYSQL_USER_NAME'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
exit
EOF

# Creating DB,tables and admin user with FLASKY_ADMIN details
mysql -u $MYSQL_USER_NAME -p$MYSQL_USER_PASSWORD <<EOF

CREATE DATABASE fairy_db;
USE fairy_db;

CREATE TABLE house (
  id int NOT NULL AUTO_INCREMENT,
  short_name varchar(50) NOT NULL,
  full_name varchar(200) NOT NULL,
  address text NOT NULL,
  phone varchar(20) NOT NULL,
  email varchar(60) NOT NULL,
  contact_person varchar(200) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE kid (
  id int NOT NULL AUTO_INCREMENT,
  name varchar(40) NOT NULL,
  birthday date NOT NULL,
  house_id int DEFAULT NULL,
  PRIMARY KEY (id),
  KEY house_id (house_id),
  CONSTRAINT kid_ibfk_1 FOREIGN KEY (house_id) REFERENCES house (id)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE project (
  id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  description text NOT NULL,
  delivery_date date DEFAULT NULL,
  visit_date date DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE santa (
  id int NOT NULL AUTO_INCREMENT,
  email_address varchar(60) NOT NULL,
  password_hash varchar(60) NOT NULL,
  first_name varchar(30) NOT NULL,
  last_name varchar(30) NOT NULL,
  phone varchar(15) NOT NULL,
  role varchar(30) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT 'user',
  confirmed tinyint DEFAULT '0',
  confirmed_on datetime DEFAULT NULL,
  registered_on datetime DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY email_address (email_address),
  KEY role_id (role,id)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE gift (
  id int unsigned NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  description varchar(300) DEFAULT NULL,
  postcard_url varchar(300) DEFAULT NULL,
  kid_id int NOT NULL,
  project_id int NOT NULL,
  santa_id int DEFAULT NULL,
  status int DEFAULT NULL,
  status_updated_time datetime DEFAULT NULL,
  status_updated_by_user int DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY id_UNIQUE (id),
  KEY kid_id (kid_id),
  KEY project_id (project_id),
  KEY gift_ibfk_3 (santa_id),
  CONSTRAINT gift_ibfk_1 FOREIGN KEY (kid_id) REFERENCES kid (id),
  CONSTRAINT gift_ibfk_2 FOREIGN KEY (project_id) REFERENCES project (id),
  CONSTRAINT gift_ibfk_3 FOREIGN KEY (santa_id) REFERENCES santa (id)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO fairy_db.santa
(email_address,
password_hash,
first_name,
last_name,
phone,
role,
confirmed)
VALUES
("$FLASKY_ADMIN",
"1234567890",
"First Name",
"Last Name",
"89001112233",
"admin",
1);

exit
EOF

# Installing python3-pip and python3-env
sudo NEEDRESTART_MODE=a apt install python3-pip -y && sudo NEEDRESTART_MODE=a apt install python3-venv -y

# Cloning App from github
git clone https://github.com/dmitriyteteruk/ProjectFairy.git
export PROJECT_FOLDER="ProjectFairy"
cd ~/$PROJECT_FOLDER
# Delete unused files
rm -rf .idea/ /venv /__pycache__


# Install required libraries for Flask and MySQL
sudo NEEDRESTART_MODE=a apt-get install python3-dev default-libmysqlclient-dev build-essential -y

# Configuring Flask App
# create and activate VENV
python3 -m venv ~/$PROJECT_FOLDER/venv
. ~/$PROJECT_FOLDER/venv/bin/activate

# Install all project requirements
pip install -r ~/$PROJECT_FOLDER/requirements.txt

# Create config file with credentials for Flask App
sudo touch /etc/config.json
sudo tee -a /etc/config.json > /dev/null <<EOF
{
        "MAIL_USERNAME": "$MAIL_USERNAME",
        "SQLALCHEMY_DATABASE_URI": "$SQLALCHEMY_DATABASE_URI",
        "SECRET_KEY": "$SECRET_KEY",
        "SECRET_KEY_FOR_TOKEN": "$SECRET_KEY_FOR_TOKEN",
        "MAIL_PASSWORD": "$MAIL_PASSWORD",
        "FLASKY_ADMIN": "$FLASKY_ADMIN",
        "FLASKY_MAIL_SENDER": "$FLASKY_MAIL_SENDER"
}
EOF

# Export flask app
export FLASK_APP=~/$PROJECT_FOLDER/run.py
sudo mkdir ~/$PROJECT_FOLDER/fairy/static/uploads

## ------------------------- BUG при повторной установке ------------- #№
## Не создаются файлы NGINX ###
# Install Nginx and Gunicorn
sudo NEEDRESTART_MODE=a apt-get install nginx -y
pip install gunicorn

# Remove default Nginx config file
sudo rm /etc/nginx/sites-enabled/default

# Create Nginx config for Flask app
sudo touch /etc/nginx/sites-enabled/flask
export PUBLIC_IP_ADDRESS=`wget -qO- https://ipecho.net/plain`
export LOCAL_IP_ADDRESS=`hostname -I`
sudo tee -a /etc/nginx/sites-enabled/flask > /dev/null <<EOF
limit_req_zone \$binary_remote_addr zone=login_register:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=all:10m rate=10r/s;

server
{
        listen 80;
        server_name $HOSTNAME
                    $PUBLIC_IP_ADDRESS
					          $LOCAL_IP_ADDRESS;

        location /fairy/static/  {
                root /home/fairy/$PROJECT_FOLDER/fairy/static;
        }


        location (/login|/register) {
                limit_req zone=login_register;
                limit_req_status 444;
        }


        location / {
                proxy_pass http://localhost:8000/;
                proxy_set_header Host \$host;
                proxy_set_header X-Forwarded-Proto \$scheme;
                proxy_set_header X-Real-IP \$remote_addr;
                proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
                client_max_body_size 1M;
                limit_req zone=all burst=20 nodelay;
                limit_req_status 444;
        }
}
EOF

# Install and config supervisor
sudo NEEDRESTART_MODE=a apt install supervisor -y
sudo touch /etc/supervisor/conf.d/flask.conf
sudo tee -a /etc/supervisor/conf.d/flask.conf > /dev/null <<EOF
[program:flask]
directory=/home/fairy/$PROJECT_FOLDER
command=/home/fairy/$PROJECT_FOLDER/venv/bin/gunicorn -w 3 run:app
user=fairy
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/flask/flask.err.log
stdout_logfile=/var/log/flask/flask.out.log
EOF

sudo mkdir -p /var/log/flask
sudo touch /var/log/flask/flask.err.log
sudo touch /var/log/flask/flask.out.log

# Restart Nginx
sudo systemctl restart nginx
sleep 5

sudo supervisorctl reload

# Install UFW and setting rules
sudo NEEDRESTART_MODE=a apt install ufw -y
sudo ufw default allow outgoing
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow http/tcp
echo "y" | sudo ufw enable

echo "Congratulations! Platform Fairy has been installed!"
echo "Please vitis http://$PUBLIC_IP_ADDRESS or http://$LOCAL_IP_ADDRESS web page and use password reset function
with $FLASKY_ADMIN."
###__END__###