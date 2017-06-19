#!/bin/bash

if [ -z "$DB_NAME" ] || [ -z "$DB_USERNAME" ] || [ -z "$DB_PASSWORD" ];
then
    echo "Environment variables DB_NAME, DB_USERNAME and DB_PASSWORD must be properly configured before installation in performed"
    exit 1
fi

if [ ! -z "$1" ];
then
    ENVIRONMENT=$1
else
    ENVIRONMENT="local"
    DB_HOST="localhost"
fi

function install_certificates {
    cp /var/www/hrpt/vagrant/certs/*.crt /usr/local/share/ca-certificates/
    update-ca-certificates
}

function install_apt_dependencies {
    apt-get update -y

    apt-get install -y build-essential \
                       python-dev \
                       python-pip \
                       git \
                       libjpeg8 \
                       libjpeg8-dev \
                       libfreetype6 \
                       libfreetype6-dev \
                       libmysqlclient-dev \
                       gettext \
                       zlib1g-dev

    apt-get clean
}

function setup_mariadb {
    apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8
    add-apt-repository 'deb [arch=amd64,i386,ppc64el] http://ftp.ddg.lth.se/mariadb/repo/10.2/ubuntu xenial main'
    sudo apt-get -y update

    echo "mysql-server-5.6 mysql-server/root_password password root" | sudo debconf-set-selections
    echo "mysql-server-5.6 mysql-server/root_password_again password root" | sudo debconf-set-selections

    apt-get install -y mariadb-server

    service mysql stop
    mysql_install_db
    service mysql start
}

function install_python_dependencies {
    pip install -r /var/www/hrpt/requirements.txt
}

function setup_environment_variables {
    echo "export DJANGO_SETTINGS_MODULE=settings.$ENVIRONMENT" > /etc/profile.d/hrpt.sh
    echo "export DB_NAME=$DB_NAME" >> /etc/profile.d/hrpt.sh
    echo "export DB_USERNAME=$DB_USERNAME" >> /etc/profile.d/hrpt.sh
    echo "export DB_PASSWORD=$DB_PASSWORD" >> /etc/profile.d/hrpt.sh
    echo "export DB_HOST=$DB_HOST" >> /etc/profile.d/hrpt.sh

    source /etc/profile.d/hrpt.sh
}

function something_something_scaffolding {
    mysql -uroot -proot <<EOF
      DROP DATABASE IF EXISTS $DB_NAME;
      DROP USER IF EXISTS $DB_USERNAME;
      CREATE USER $DB_USERNAME IDENTIFIED BY '$DB_PASSWORD';
      CREATE DATABASE $DB_NAME;
      GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USERNAME'@'%';
EOF

    cd /var/www/hrpt/
    python manage.py migrate --noinput
    python manage.py loaddata db/fixtures.json
    python manage.py shell -c "from apps.pollster.models import Survey; Survey.objects.get(shortname='intake').publish()"
}


install_certificates
install_apt_dependencies

if [ $ENVIRONMENT == "local" ];
then
    setup_mariadb
fi

install_python_dependencies
setup_environment_variables
something_something_scaffolding
