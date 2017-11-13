# -*- mode: ruby -*-
# vi: set ft=ruby :

# Set up an Ansible Controller host with DebOps support using Vagrant
#
# Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017 DebOps project https://debops.org/


# Basic usage:
#
#     vagrant up && vagrant ssh
#     cd src/controller ; debops


# Configuration variables:
#
#     VAGRANT_BOX="debian/stretch64"
#         Specify the bos to use.
#
#     VAGRANT_HOSTNAME="stretch"
#         Set a custom hostname after the box boots up.
#
#     CONTROLLER=false
#         Set to 'true' to set up a configuration with normal Diffie-Hellman
#         parameters (3072, 2048) instead of a smaller one (1024). Initial DH
#         parameter generation may take a long time.
#
#     APT_CACHE=""             (http://apt.example.org:3142)
#         Set a custom APT cache URL inside the Vagrant box.


$set_environment_variables = <<SCRIPT
tee "/etc/profile.d/vagrant_vars.sh" > "/dev/null" <<EOF
export VAGRANT_ENVIRONMENT="true"
EOF
SCRIPT

$set_apt_cache = <<SCRIPT
if [ -n "#{ENV['APT_CACHE']}" ] ; then
    printf "%s\n" "Configuring APT cache at '#{ENV['APT_CACHE']}'..."
    cat <<EOF | sudo tee /etc/apt/apt.conf.d/00aptproxy
Acquire::http::Proxy "#{ENV['APT_CACHE']}";
EOF
fi
SCRIPT

$set_hostname = <<SCRIPT
if [ -n "#{ENV['VAGRANT_HOSTNAME']}" ] ; then
    export REAL_HOSTNAME="#{ENV['VAGRANT_HOSTNAME']}"
fi

if [ -n "${REAL_HOSTNAME}" ] ; then
    printf "%s\n" "Changing the hostname to '${REAL_HOSTNAME}'..."
    if [ -d /run/systemd/system ] ; then
        hostnamectl set-hostname ${REAL_HOSTNAME}
        systemctl restart networking.service
    else
        hostname ${REAL_HOSTNAME}
        echo "${REAL_HOSTNAME}" > /etc/hostname
        /etc/init.d/networking restart
    fi
fi
SCRIPT

$bootstrap_ansible_controller = <<SCRIPT
set -o nounset -o pipefail -o errexit

if ! [ -h .local/share/debops/debops ] ; then
    mkdir -p src .local/share/debops
    ln -s /vagrant .local/share/debops/debops
fi

if ! type ansible > /dev/null 2>&1 ; then
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get --no-install-recommends -yq install python-pip python-wheel python-setuptools vim ranger tree encfs sshfs
    sudo pip install pycodestyle unittest2 nose2 cov-core sphinx_rtd_theme yamllint ansible debops
fi

if ! [ -d src/controller ] ; then
    debops-init src/controller
    sed -i '/ansible_connection=local$/ s/^#//' src/controller/ansible/inventory/hosts
    mkdir -p "src/controller/ansible/inventory/host_vars/$(hostname)"
    if [ -z "#{ENV['CONTROLLER']}" ] || [ "#{ENV['CONTROLLER']}" != "true" ] ; then
        echo "---\n\n# Use smaller DH parameters to speed up test runs\ndhparam__bits: [ '1024' ]" > "src/controller/ansible/inventory/host_vars/$(hostname)/dhparam.yml"
    fi
fi
SCRIPT

Vagrant.configure("2") do |config|

  config.vm.box = ENV['VAGRANT_BOX'] || 'debian/stretch64'

  config.vm.provision "shell", inline: $set_environment_variables
  config.vm.provision "shell", inline: $set_apt_cache
  config.vm.provision "shell", inline: $set_hostname
  config.vm.provision "shell", inline: $bootstrap_ansible_controller, privileged: false

  if Vagrant.has_plugin? 'vagrant-cachier'
    config.cache.enable :apt
    config.cache.scope = :box
  end

end
