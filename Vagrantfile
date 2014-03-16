# -*- mode: ruby -*-
# vim: ft=ruby

# Vagrantfile for ginas project
# https://github.com/ginas/ginas/

# Default ginas inventory
defined?(GINAS_INVENTORY) or GINAS_INVENTORY = "lemp"

# Load Vagrantfile from selected Vagrant inventory
begin
    load "contrib/vagrant/inventory-" + GINAS_INVENTORY + "/Vagrantfile"
rescue LoadError
    # ignore
end


