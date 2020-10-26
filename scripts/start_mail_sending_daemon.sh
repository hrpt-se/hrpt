#!/usr/bin/env bash

. /etc/profile.d/hrpt.sh
/usr/bin/python3 /var/www/hrpt/manage.py send_queued_emails
