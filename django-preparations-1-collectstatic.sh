#!/bin/bash

#Detta ska köras för att autogenerera alla statiska filer som Webbservern kan leverera direkt:
python3 manage.py collectstatic --noinput
