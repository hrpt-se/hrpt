#!/bin/bash

if [ -z "$DB_NAME" ] || [ -z "$DB_USERNAME" ] || [ -z "$DB_PASSWORD" ];
then
    echo "Environment variables DB_NAME, DB_USERNAME and DB_PASSWORD must be properly configured before installation in performed"
    exit 1
fi

while getopts e: opt; do
    case $opt in
        e)
            ENVIRONMENT=$OPTARG
            ;;
    esac
done

if [ -z "$ENVIRONMENT" ] || [ $ENVIRONMENT == "local" ];
then
    DB_HOST="localhost"
    WEB_HOST="localhost"
    ENVIRONMENT="local"
else
    if [ -z "$WEB_HOST" ];
    then
        echo "When ENVIRONMENT is not local, WEB_HOST must be set"
    fi
fi


function install_certificates {
    cp /var/www/hrpt/vagrant/certs/*.crt /usr/local/share/ca-certificates/
    update-ca-certificates
}

function install_apt_dependencies {
    apt-get update -y

    apt-get install -y build-essential \
                       python3-dev \
                       python3-pip \
                       git \
                       libjpeg8 \
                       libjpeg8-dev \
                       libfreetype6 \
                       libfreetype6-dev \
                       gettext \
                       zlib1g-dev \
                       libssl-dev \
                       python3-mysqldb \
                       gdal-bin \
                       python3-gdal

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

    # move to it's own command and
    # remove IF EXISTS since it is not supported for MySQL<5.7
    mysql -uroot -proot <<EOF
      DROP USER $DB_USERNAME;
EOF

    mysql -uroot -proot <<EOF
      DROP DATABASE IF EXISTS $DB_NAME;
      CREATE USER $DB_USERNAME IDENTIFIED BY '$DB_PASSWORD';
      CREATE DATABASE $DB_NAME CHARACTER SET = 'utf8' COLLATE = 'utf8_bin';
      GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USERNAME'@'%';
EOF
}

function install_python_dependencies {
    export LDFLAGS="-L/usr/local/opt/openssl/lib $LDFLAGS"
    export CPPFLAGS="-I/usr/local/opt/openssl/include $CPPFLAGS"
    pip3 install -r /var/www/hrpt/requirements.txt
}

function setup_environment_variables {
    echo "export DJANGO_SETTINGS_MODULE=settings.$ENVIRONMENT" > /etc/profile.d/hrpt.sh
    echo "export DB_NAME=$DB_NAME" >> /etc/profile.d/hrpt.sh
    echo "export DB_USERNAME=$DB_USERNAME" >> /etc/profile.d/hrpt.sh
    echo "export DB_PASSWORD=$DB_PASSWORD" >> /etc/profile.d/hrpt.sh
    echo "export DB_HOST=$DB_HOST" >> /etc/profile.d/hrpt.sh
    echo "export WEB_HOST=$WEB_HOST" >> /etc/profile.d/hrpt.sh

    source /etc/profile.d/hrpt.sh
}

function setup_apache {
    apt-get install -y apache2 \
                       libapache2-mod-wsgi

    git clone https://github.com/hrpt-se/hrpt.git -b feature/el-deployment-preparation /var/www/hrpt/
    cd /var/www/hrpt/
    cp vagrant/000-hrpt.conf /etc/apache2/sites-available/
    cp vagrant/001-hrpt-prod-redirect.conf /etc/apache2/sites-available/
    echo '. /etc/profile.d/hrpt.sh' >> /etc/apache2/envvars
    a2dissite 000-default
    a2ensite 000-hrpt 001-hrpt-prod-redirect
    service apache2 restart
}

function create_data_directories {
    mkdir -p /var/lib/hrpt/upload
    mkdir -p /var/lib/hrpt/static

    chown -R www-data:www-data /var/lib/hrpt
    chmod 775 /var/lib/hrpt/*
    usermod -a -G www-data ubuntu
}

function setup_django_scaffolding {
    cd /var/www/hrpt/
    python3 manage.py migrate --noinput
    python3 manage.py collectstatic --noinput
}

function install_fixtures {
    python3 manage.py loaddata db/fixtures.json
    python3 manage.py shell -c "from apps.pollster.models import Survey;Survey.objects.get(shortname='intake').unpublish(); Survey.objects.get(shortname='intake').publish()"
}

function start_mail_service {
    cp vagrant/hrpt-mail.service /etc/systemd/system/
    systemctl enable hrpt-mail
}

install_certificates
install_apt_dependencies

if [ $ENVIRONMENT == "local" ];
then
    setup_mariadb
fi


setup_environment_variables

if [ $ENVIRONMENT != "local" ];
then
    setup_apache
fi

create_data_directories
install_python_dependencies
setup_django_scaffolding

if [ $ENVIRONMENT == "local" ];
then
    install_fixtures
fi

start_mail_service
