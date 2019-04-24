# OPTIONS #
# ======= #

$vagrant_box = "ubuntu/trusty64"
$guest_port = 5000
$host_port = 5000
$ansible_verbose = false

# ======= #

Vagrant.configure("2") do |config|

    config.vm.box = $vagrant_box
    config.vm.network "forwarded_port", guest: $guest_port, host: $host_port

    config.vm.provision "ansible_local" do |ansible_up|
        ansible_up.playbook = "ansible/provision.yml"
        ansible_up.verbose = $ansible_verbose
    end

    config.trigger.before :destroy do |destroy|
        destroy.run_remote = {inline: "ansible-playbook --connection=local --inventory 127.0.0.1, /vagrant/ansible/destroy.yml"}
    end

end
