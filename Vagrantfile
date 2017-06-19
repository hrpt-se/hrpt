Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/xenial64"
    config.vm.provision :shell, path: "install.sh", env: {
        "DB_NAME" => "epiwork",
        "DB_USERNAME" => "epiwork",
        "DB_PASSWORD" => "epiwork"
    }
    config.vm.network :forwarded_port, guest: 8000, host: 8000
    config.vm.synced_folder ".", "/var/www/hrpt"
end
