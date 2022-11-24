#!/bin/bash

#Testar om Django-konfigurationen är redo för deployment:
python3 manage.py check --deploy

#Testar Django-CMS:
python3 manage.py cms check