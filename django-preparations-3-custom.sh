#!/bin/bash

python3 manage.py loaddata db/fixtures.json
python3 manage.py shell -c "from apps.pollster.models import Survey;Survey.objects.get(shortname='intake').unpublish(); Survey.objects.get(shortname='intake').publish()"
