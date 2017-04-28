#!/bin/bash

DB_NAME="epiwork"
DB_USERNAME="epiwork"
DB_PASSWORD="epiwork"

# Install custom certificates
cp /vagrant/vagrant/certs/*.crt /usr/local/share/ca-certificates/
update-ca-certificates

# Install dependencies from apt
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

# Update PostgreSQL configuration to allow md5 authentication without password for user admin
cp /vagrant/vagrant/pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
service postgresql restart
echo "*:*:$DB_NAME:$DB_USERNAME:$DB_PASSWORD" >> ~/.pgpass
chmod 600 ~/.pgpass

# Install Python dependencies
pip install -r /vagrant/requirements.txt

# Drop DB (if existing) and recreate from dump-file and migration files
sudo -u postgres psql <<EOF
  DROP DATABASE IF EXISTS $DB_NAME;
  DROP USER IF EXISTS $DB_USERNAME;
  CREATE USER $DB_USERNAME WITH PASSWORD '$DB_PASSWORD' SUPERUSER;
  CREATE DATABASE $DB_NAME WITH OWNER = $DB_USERNAME;
EOF

psql --username=$DB_USERNAME $DB_NAME < /vagrant/db_dump.sql

for migration in `find /vagrant/db/migrations -name "*.sql" | sort`; do
  psql --username=$DB_USERNAME $DB_NAME -w -f $migration
done
