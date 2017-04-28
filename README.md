# hrpt


The documentation is not here!

So far it's on the network share.


## Running the site
The site is prepared to be developed in VirtualBox, provisioned by Vagrant. To run it locally, you need to install VirtualBox and Vagrant on your local computer. Download and install from https://www.virtualbox.org/wiki/Downloads and https://www.vagrantup.com/downloads.html or through your favorite package manager.

When VirtualBox and Vagrant is installed, running the site is as easy as bringing up a terminal window and issuing:
```bash
$ cd <folder where the repo is cloned>
$ vagrant up
```

After the setup is completed you can start the Django server by logging in to the machine using ssh:
```bash
$ vagrant ssh
Welcome to Ubuntu 14.04.5 LTS (GNU/Linux 3.13.0-117-generic x86_64)
[...]

vagrant@vagrant-ubuntu-trusty-64:~$ cd /vagrant/
vagrant@vagrant-ubuntu-trusty-64:/vagrant$ python manage.py runserver 0.0.0.0:8000
Validating models...

0 errors found
Django version 1.3.3, using settings 'vagrant.settings'
Development server is running at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

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
$ vagrant box add "ubuntu/trusty64"
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


## TODO

 * define pip dependencies
 * save migration state on a database table
 * Add link to my first commit, so old code can be easily reached, no need to
 * remove internacionalization. It is adding a huge usability buron on the system.
 * Re-implment the whole survey thing using reactive.js. OR other,  althought I strongly suggest reactive.js if we want to avoid bloat
 * make the apache script accept a host
 * try the bootstrap script with a PASSWORD environment variable (experiment)
