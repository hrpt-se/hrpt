# HRPT Stage Deployment Guide

This guide outlines the process of setting up the HRPT system on a stage server. 
There are two major parts of the process: Setting up the Django based system 
and migrating data from a running production system.

## Installing the system

*Prerequisites:*
  - Installed Ubuntu 16.04 base system
  - Access to MariaDB database

Installation of the system is easy once the prerequisites are met. There is an
installation script that can be downloaded from the HRPT repo. The script 
requires the database configuration as environment variables. Once they are in
place, the installer can be run. See example below.

The installer script will install and configure all required software to run 
the HRPT system on a stage server, including Python, Django and Apache.

```bash
$ export DB_NAME=<db-name> 
$ export DB_USERNAME=<username> 
$ export DB_PASSWORD=<password>
$ export DB_HOST=<db-hostname>
$ export WEB_HOST=<webserver-hostname>
$ curl https://raw.githubusercontent.com/hrpt-se/hrpt/feature/el-deployment-preparation/install.sh | sudo -E bash -s -- -e stage
```

Once the installer finishes, the system should be accessible on port 80 on the 
server.

## Mail sending daemon
The system contains a daemon that sends mail which are queued in the database. 
More info on how the daemon is deployed and controlled can be found in the readme file.

## Migrating data (Optional)

Migrating data from an existing system needs to be performed in two steps. 
First migrating all user- and survey data. Survey responses needs to be 
migrated separately.

Note that CMS data can't be migrated from existing production systems to more 
recent versions due to backwards incompatibilities.

First log in to the existing system and use Django's `dumpdata` management 
command to export all relevant data in json format. See example below:

```bash
$ python manage.py dumpdata --natural \
                            --exclude auth.permission \
                            --exclude contenttypes \
                            --exclude survey.profile \
                            --exclude survey.lastresponse \
                            --exclude survey.surveylistplugin \
                            auth \
                            pollster \
                            survey \
                            accounts > hrpt_data.json
```

Take the exported json-file and transfer it to the stage server. Then load the
exported to the target server. Apply the data using the `loaddata` command. 

```bash
$ python manage.py loaddata hrpt_data.json
```