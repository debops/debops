# -*- mode: ruby -*-
# vi: set ft=ruby

# Vagrantfile for ginas project
# https://github.com/drybjed/ginas/

VAGRANTFILE_API_VERSION = '2'

DOMAIN = '.nat.example.com'
NETWORK = '192.168.50.'
NETMASK = '255.255.255.0'

# Source: https://github.com/drybjed/vagrant-debian-wheezy-64/tree/ginas
DEFAULT_BOX = 'debian-wheezy-amd64-netinst'
DEFAULT_BOX_URL = 'https://dl.dropboxusercontent.com/u/55426468/debian-wheezy-amd64-netinst.box'

# Fix permissions of vagrant's insecure SSH key
system('chmod 0600 contrib/vagrant/ssh/id_rsa_insecure')


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = DEFAULT_BOX
  config.vm.box_url = DEFAULT_BOX_URL

  # LEMP webserver (Linux, nginx, MySQL, PHP5)
  config.vm.define :web do |web|
    web.vm.hostname = 'web' + DOMAIN
    web.vm.network :private_network, ip: NETWORK + "10", :netmask => NETMASK
  end

  # MySQL server with PHPMyAdmin
  config.vm.define :db do |db|
    db.vm.hostname = 'db' + DOMAIN
    db.vm.network :private_network, ip: NETWORK + "20", :netmask => NETMASK
  end

  # Ansible Controller
  config.vm.define :master do |master|
    master.vm.hostname = 'master' + DOMAIN
    master.vm.network :private_network, ip: NETWORK + "2", :netmask => NETMASK

    config.vm.provision "ansible" do |ansible|
      ansible.host_key_checking = false
      ansible.inventory_path = "contrib/vagrant/inventory"
      ansible.playbook = "playbooks/site.yml"
    end
  end

end


