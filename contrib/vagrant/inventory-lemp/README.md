# Ansible + Vagrant = LEMP

This is a combined [Ansible](http://ansible.com/) inventory directory and [Vagrant](http://vagrantup.com/)'s Vagrantfile, utilizing ginas playbook as a base to create a set of 3 virtual machines - a master control server, a webserver and a database server, with [VirtualBox](http://virtualbox.org/) as the underlying virtualization platform.

## Overview

**master**.nat.example.com (IP address `192.168.50.2`) is a "control server". It has installed [Ansible](https://github.com/ansible/ansible/) from current `devel` branch and, recursively, [ginas](https://github.com/ginas/ginas/) from the master branch with "lemp" inventory enabled as the default.

Root directory of `ginas` project from hosting server will be mounted by Vagrant as `/home/vagrant/ginas/`.

**web**.nat.example.com (IP address `192.168.50.10`) is a webserver with configured [nginx](http://nginx.org/) and [PHP5](http://php.net/). On the `web` server will be installed PostgreSQL database, currently in testing phase.

Directory `contrib/vagrant/src/` inside the `ginas` repository will be mounted by Vagrant as `/srv/www/sites/default/` which corresponds to the webserver's document root - all documents put in `public/` directory inside that path will be automatically accessible over HTTP and HTTPS on the IP address of the server.

**db**.nat.example.com (IP address `192.168.50.20`) is a database server with MySQL 5.5 database installed by default and accessible from the local network (192.168.50.0/24). Access to the MySQL database is also possible using installed PHPMyAdmin served by nginx webserver.

All servers are configured to allow access via SSH to `vagrant` account using [insecure SSH key](https://github.com/mitchellh/vagrant/tree/master/keys), which is also available in ginas repository as `contrib/vagrant/ssh/id_rsa_insecure`. Additionally, if servers have been configured from the local server instead of the `master` server (bootstrapped), `vagrant` account will be accessible using user's own SSH keys, and user's own account will be created on each server, with full `sudo` access. All accounts (`root` included) will have configured [dotfiles](https://github.com/drybjed/dotfiles/) by default, with zsh, vim, tmux and git configuration and full UTF-8 support.

## Installation and configuration

You should have installed and configured Vagrant, git, VirtualBox. Ansible is not required on the hosting server, but makes things easier. Don't forget to install Vagrant support for Ansible.

Clone `ginas` repository to a directory and cd into it:

    git clone https://github.com/ginas/ginas/ && cd ginas

LEMP repository is configured as the default in `ginas`, so now all you need to do to start it, is:

    vagrant up --no-provision

`--no-provision` option might be helpful here, because Vagrant tends to provision each server separately - by adding that option you allow all three servers to start up at once. When all servers are up and running, and Ansible is available on the localhost, you can start provisioning:

    vagrant provision

You might be asked to accept remote host's SSH fingerprints or Ansible might inform you about insecure SSH fingerprints - this is normal. In that case just run above command again, and Ansible should start provisioning your new servers.

Depending on your server parameters and network connection, provisioning will take several minutes to finish. After that you can login to the servers by using command:

    vagrant ssh [master|web|db]

To get access to `root` account, use `sudo su`.


