# hrpt

## Running the system
The easiest way to deploy the system on your local machine for development is to use Vagrant. To run it locally, you need to install VirtualBox and Vagrant on your local computer. Download and install from https://www.virtualbox.org/wiki/Downloads and https://www.vagrantup.com/downloads.html or through your favorite package manager. If you want to deploy the system in a server settings, that is documented in the docs-folder.

When VirtualBox and Vagrant is installed, running the site is as easy as bringing up a terminal window and issuing:
```bash
$ cd <folder where the repo is cloned>
$ vagrant up
```

After the setup is completed you can start the Django server by logging in to the machine using ssh:
```bash
$ vagrant ssh
Welcome to Ubuntu 16.04.2 LTS (GNU/Linux 4.4.0-87-generic x86_64)
[...]

ubuntu@ubuntu-xenial:~$ cd /var/www/hrpt/
ubuntu@ubuntu-xenial:/var/www/hrpt$ python manage.py runserver 0.0.0.0:8000
Validating models...

0 errors found
Django version 1.10.7, using settings 'settings.local'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### Mail sending daemon
The system contains a daemon responsible for sending mails which are queued in the database. The daemon is installed and started by the installation script which is executed by Vagrant. The daemon is controlled by Systemd and can be controlled 
by running `systemctl <command> hrpt-mail` where `<command>` is either of `status` `start` `stop`or `restart`.
Check the log files with `sudo journalctl -u hrpt-mail`


### SSL certificate workaround
If you are trying to run `vagrant up` in a network that intercepts SSL traffic, you will likely face an error message:
> The box 'ubuntu/trusty64' could not be found or could not be accessed in the remote catalog. If this is a private box on HashiCorp's Atlas, please verify you're logged in via `vagrant login`. Also, please double-check the name. The expanded
> URL and error message are shown below:
>
> URL: ["https://atlas.hashicorp.com/ubuntu/trusty64"]
> Error: SSL certificate problem: self signed certificate in certificate chain
> More details here: http://curl.haxx.se/docs/sslcerts.html

To work around this problem:
  1. Retrieve the root certificates for the network in PEM format with .crt suffix and place in the vagrant/certs/ folder
  2. Download the Ubuntu box without SSL certificate validation and then set up the environment.
```bash
$ vagrant box add "ubuntu/trusty64" --insecure
==> box: Loading metadata for box 'ubuntu/trusty64'
    box: URL: https://atlas.hashicorp.com/ubuntu/trusty64
==> box: Adding box 'ubuntu/trusty64' (v20170422.0.0) for provider: virtualbox
    box: Downloading: https://atlas.hashicorp.com/ubuntu/boxes/trusty64/versions/20170422.0.0/providers/virtualbox.box
    box: Progress: 100% (Rate: 11.2M/s, Estimated time remaining: --:--:--)
==> box: Successfully added box 'ubuntu/trusty64' (v20170422.0.0) for 'virtualbox'!
$ vagrant up
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'ubuntu/trusty64'...
[...]
```
Use the steps in this article to add the root cert to the CA store used by pip
https://stackoverflow.com/questions/39356413/how-to-add-a-custom-ca-root-certificate-to-the-ca-store-used-by-pip-in-windows


## Settings
The site uses different settings depending on the environment and all setting files are stored in the settings folder.
The file `base.py` file contains common settings for all environments and should never be used directly. The `local.py` 
file is intended for development.

### Environment variables.
There are a number of environment variables that configures the site. The install script will assign values to the variables 
and store them in `/etc/profile.d/hrpt.sh`, making sure that they are populated in supported shells.

  - `DJANGO_SETTINGS_MODULE`: Which settings module that should be loaded. Should be `settings.local`for development.
  - `DB_HOST`: The hostname of the database server. `localhost` for development.
  - `DB_USER`: Which username to use when connecting to the database 
  - `DB_PASSWORD`: The password to use when authentication against the database server
  - `DB_NAME`: The name of the database to use

### Secrets
Any settings that should be kept out of git (for example the secet key or API keys) can be stored in a file named `secrets.py` 
in the settings directory. There is a `secrets.py.template` file that can be used as a template, containing more info.

### Upgrade to Django 1.11 and Django CMS 3.5
`cd /var/www/hrpt`
`pip install -upgrade pip`
`sudo pip install -r requirements.txt `
Todo: Check if sudo is necessary
Perform migrations:

`python manage.py migrate  # to ensure that your database is up-to-date with migrations
python manage.py cms fix-tree`
