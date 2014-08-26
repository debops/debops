# -*- mode: ruby -*-
# vim: ft=ruby

# Vagrantfile for DebOps project
# http://debops.org/

# Default DebOps inventory
defined?(DEBOPS_INVENTORY) or DEBOPS_INVENTORY = "single"
#defined?(DEBOPS_INVENTORY) or DEBOPS_INVENTORY = "lemp"

# Load Vagrantfile from selected Vagrant inventory
begin
    load "contrib/vagrant/inventory-" + DEBOPS_INVENTORY + "/Vagrantfile"
rescue LoadError
    # ignore
end


