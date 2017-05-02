Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/xenial64"
    config.vm.provision :shell, path: "install.sh"
    config.vm.network :forwarded_port, guest: 8000, host: 8000
end
