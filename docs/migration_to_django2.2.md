# Migration to Django 2.2
Older versions of pip tends to install the latest version of package dependencies.
This can be dangerous since it will most likely break things. For example it can install packages
that require Python 3 while the app as a whole runs Python 2. With this said pip should be kept up to date.

Migrating from Django<1.11 to 2.2 requires the migration to be split into multiple steps due to dependencies,
mainly Django CMS, requiring the database to be up to date with the previous version.
With Django 2.2 there is also a requirement that Python 3.X is used which is also part of the migration.

### Initial steps
The first step to get to Django 2.2 is to upgrade Django to the latest LTS version, 1.11.
For this step to be possible, all the used dependencies have to support this version of Django.
This is not not the case for Django CMS 3.4.4 which will have to be upgraded to 3.5.4.

##### Django CMS 3.5
Upgrading to CMS 3.5.4 is easily achieved by following a few manual steps.
[Django CMS upgrade information](http://docs.django-cms.org/en/latest/upgrade/index.html)

Before starting the upgrade of Django CMS it is highly advised to make a backup of the the database.

```shell script
python manage.py migrate  # to ensure that your database is up-to-date with migrations
python manage.py cms fix-tree
```
Before proceeding to the next step, make sure that dependencies such as CMS plugins are working as intended.

It is also important to make sure that `pip` is up to date to avoid dependencies being updated to unsupported versions.

```shell script
pip install django-cms==<target version>
```

After installing the new CMS version all that remains is to apply the changes to the database.

```shell script
python manage.py migrate  # to apply the new migrations
```

##### Django 1.11
With the CMS dependency updated we now upgrade Django to 1.11.
This requires that new code is pulled from the branch `feature/django1.11-cms3.5`.
Following this we run `sudo -E bash install.sh` on the server to install the new libs and dependencies.
When this has completed the server will be running the new version of Django.

> install.sh might have Windows line endings which can make the script unable to run.
> To fix this run `sed -i 's/\r//' install.sh` to replace them with Linux ones.

### Python 3
Upgrading from Python 2 to 3 requires some code changes, present on the branch
`python3.5`. All that is required is to pull this branch and then run `sudo -E bash install.sh`
on the server. This will install all required dependencies and libraries.

### Final steps
The final steps of the upgrade is to get from Django 1.11 to Django 2.2. This also requires
the CMS to be upgraded.

##### Django CMS 3.7
With Python upgraded, we need to upgrade Django CMS again to support Django 2.2.
This process is the same as the [previous upgrade](#django-cms-35) with `python` and `pip`
being replaced with `python3` and `pip3`. The target version for Django CMS this time will be `3.7.4`. 

##### Django 2.2
The final step is to upgrade Django itself. This is achieved by switching to the branch `feature/django2.2-cms3.7`
which contains all necessary code changes, fixes and dependency updates.

Running `sudo -E bash install.sh` with the new `install.sh` will then update everything that needs updating. 
