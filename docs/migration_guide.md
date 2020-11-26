# Server setup

### Create a new user
```shell script
sudo adduser --disabled-password hrpt
sudo gpasswd -a hrpt www-data
```

### Create directories
```shell script
sudo mkdir -p /var/www/hrpt
sudo chown hrpt:www-data /var/www/hrpt

sudo setfacl -d -m g::rX /var/www/hrpt
sudo setfacl -d -m o::--- /var/www/hrpt
sudo chmod g+s /var/www/hrpt
```

### Clone git repo
```shell script
cd /var/www/hrpt
sudo -u hrpt git clone https://github.com/hrpt-se/hrpt.git .
```

### Create environment variables
```shell script
sudo su
export DB_NAME=<db-name> 
export DB_USERNAME=<username> 
export DB_PASSWORD=<password>
export DB_HOST=<db-hostname>
export WEB_HOST=<webserver-hostname>
```

### Setup

#### Fix broken dependencies
The following must change in `requirements.txt`:
```shell script
Add/uncomment       mysqlclient==1.3.10
Change cms version  djangocms==3.4.5
Add                 djangocms-attributes-field==1.1.0
``` 
Install mysql client:
```shell script
sudo apt-get install default-libmysqlclient-dev
```

#### Installation
```shell script
sudo pip install -U pip
sudo -E ./install.sh -e stage
sudo chmod +x install.sh
sudo a2dissite 001-hrpt-prod-redirect
systemctl reload apache2
```

#### Fix the broken Django package
```shell script
nano /usr/local/lib/python2.7/dist-packages/django/contrib/gis/geos/libgeos.py
```
Find the function `geos_version_info` towards the bottom. Replace the line `ver = geos_version().decode()` with
`ver = geos_version().decode().split(" ")[0]`.

#### Create a secrect file
```shell script
nano /var/www/hrpt/settings/secrets.py
```

Add the following to the new file before saving it:
```shell script
NORECAPTCHA_SITE_KEY = ""
NORECAPTCHA_SECRET_KEY = ""
GA_TRACKING_ID = ""  # can be excluded if Google Analytics is not required 
```

### Migration

#### Step 1 (CMS 3.5 & Django 1.11)
```shell script
sudo su hrpt
python manage.py migrate
python manage.py cms fix-tree
sudo pip install django-cms==3.5.4      # exit impersonation
sudo su hrpt
python manage.py migrate
git checkout feature/django1.11-cms3.5

# Exit impersonation of hrpt
sudo chmod +x install.sh
sudo ./install.sh -e stage              # prod if in production
sudo service apache2 start              # just in case
```

#### Step 2 (Python 3)
```shell script
sudo -u hrpt git checkout python3.5
sudo chmod +x install.sh
sudo ./install.sh -e stage
sudo service apache2 start              # just in case
```

#### Step 3 (CMS 3.7)
```shell script
sudo su hrpt
python3 manage.py migrate
python3 manage.py cms fix-tree
sudo pip3 install django-cms==3.7.4     # as root
sudo su hrpt
python3 manage.py migrate
sudo service start apache2              # as root
```

#### Step 4 (Django 2.2)
```shell script
sudo -u hrpt checkout feature/django2.2-cms3.7
sudo ./install.sh -e stage
sudo service start apache2 
```
