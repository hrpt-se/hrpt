#!/bin/bash

apt-get update -y

apt-get install -y build-essential \
                   python-dev \
                   python-pip \
                   git \
                   postgresql-9.3 \
                   postgresql-contrib-9.3 \
                   postgresql-client-9.3 \
                   postgresql-server-dev-9.3 \
                   libjpeg8 \
                   libjpeg8-dev \
                   libfreetype6 \
                   libfreetype6-dev \
                   gettext \
                   zlib1g-dev

apt-get clean

cp /vagrant/vagrant/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
service postgresql restart

echo "*:*:epiwork:admin:admin" >> ~/.pgpass
chmod 600 ~/.pgpass

pip install -r /vagrant/requirements.txt


sudo -u postgres psql <<EOF
  DROP DATABASE IF EXISTS epiwork;
  DROP USER IF EXISTS admin;
  CREATE USER admin WITH PASSWORD 'admin' SUPERUSER;
  CREATE DATABASE epiwork WITH OWNER = admin;
EOF

psql --username=admin epiwork < /vagrant/db_dump.sql

for migration in `find /vagrant/db/migrations -name "*.sql" | sort`; do
  psql --username=admin epiwork -w -f $migration
done
