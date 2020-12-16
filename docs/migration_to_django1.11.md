Branch feature/update_install

Initial goal: Get the vagrant environment to work again after migrating to new computer.
The original setup with a "vagrant up" from the master branch did not work anymore.

It seems like there are major changes in the libraries that break stuff.

First changed from mysqlclient to mysql-connector.
Mysqlclient does not seem to work anymore.

Reoved libmysqlclient-dev  from the apt install list in install.sh
Added:     libssl-dev  (some install complained about this)
           python-mysqldb (for the mysql-connector)
           gdal-bin (completely unclear, but looks like new requirement from Django-CMS )
           python-gdal 
           
As it did now work anyhow. Moved on to updating to Django 1.11 adn Django CMS 3.5 or higher.

After update of Django and Django CMS an migration of the database is needed.
Run 'python manage.py migrate' to apply migration.