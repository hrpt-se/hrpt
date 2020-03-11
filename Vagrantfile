Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/xenial64"
    config.vm.provision :shell, path: "install.sh", env: {
        "DB_NAME" => "epiwork",
        "DB_USERNAME" => "epiwork",
        "DB_PASSWORD" => "epiwork"
    }
    config.vm.network :forwarded_port, guest: 8000, host: 8000
    config.vm.synced_folder ".", "/var/www/hrpt"
    config.ssh.guest_port = 2222

    # In case the mount has dragged, restart the mail sending daemon to make
    # sure that the daemon can start properly
    config.vm.provision "shell", run: "always", inline: "sleep 10; systemctl restart hrpt-mail"
end
