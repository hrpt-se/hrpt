#!/bin/bash

#Detta ska köras varje gång man uppgraderat Django-versionen
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput
#Behövs för Django-CMS:
python3 manage.py cms fix-tree