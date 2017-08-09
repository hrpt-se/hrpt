#!/usr/bin/env bash

. /etc/profile.d/hrpt.sh
/usr/bin/python /var/www/hrpt/manage.py send_queued_emails
