#! /usr/bin/env python

import os
import subprocess
import socket
from optparse import OptionParser

VERSION = "0.1.0"
DEFAULT_APT_PACKAGES = "git lsb-release make"
GINAS_CLONE_URL = "https://github.com/ginas/ginas.git"

parser = OptionParser(version="%prog v{0}".format(VERSION))

parser.add_option("-a", "--apt-host-packages",
                  dest="apthostpackages",
                  help="Quoted space separated list of extra packages that you want installed on this machine",
                  metavar="PACKAGES")
parser.add_option("-i", "--install-path",
                  dest="installpath",
                  help="The ginas installation path",
                  metavar="PATH")
parser.add_option("-f", "--force-install-ansible",
                  action="store_true",
                  dest="forceinstallansible",
                  help="Forcefully install ansible even if it exists",
                  metavar="True")
parser.add_option("-d", "--domain-name",
                  dest="domainname",
                  help="The domain name added to /etc/hosts",
                  metavar="DOMAIN_NAME")

(options, args) = parser.parse_args()

class CLI:
  def __init__(self, options, args):
    self.options = options
    self.args = args

    self.hostname = socket.gethostname()

    if self.options.installpath is None:
      self.log_error("You must supply an installation path, example: -i /tmp/foo")
      quit()

    if self.options.domainname is None:
      self.log_error("You must supply a domain name, example: -d {0}.dev".format(self.hostname))
      quit()

    self.ginas_install_path = os.path.join(self.options.installpath, "ginas")
    self.ginas_inventory_path = os.path.join(self.ginas_install_path, "inventory")

    if os.path.exists(self.ginas_install_path):
      self.log_error("Ginas has already been installed to: {0}".format(self.ginas_install_path))
      quit()

  def install_default_apt_packages(self):
    self.log_task("Install default apt packages:")

    self.shell("sudo apt-get install -y {0}".format(DEFAULT_APT_PACKAGES))

  def install_ginas(self):
    self.log_task("Install ginas:")

    self.shell("git clone {0} {1}".format(GINAS_CLONE_URL, self.ginas_install_path))
    self.shell("mkdir -p {0}/group_vars {0}/host_vars".format(self.ginas_inventory_path))
    self.shell("touch {0}/hosts".format(self.ginas_inventory_path))

  def install_ansible(self):
    proc = subprocess.Popen(["ansible --version"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    if (len(out) == 0 or self.options.forceinstallansible):
      self.log_task("Install ansible:")
      self.shell("{0}/contrib/bootstrap-ansible.sh".format(self.ginas_install_path))

  def update_etc_hosts(self):
    etchosts_path = "/etc/hosts"

    self.log_task("Update {0}".format(etchosts_path))

    self.shell("mkdir -p /tmp{0}".format(etchosts_path))
    self.shell("cp {0} /tmp{0}.tmp".format(etchosts_path))

    fo = open("/tmp{0}.tmp".format(etchosts_path), "a")
    fo.write("\n127.0.0.1 {0} {1}\n".format(self.options.domainname, self.hostname))
    fo.close()

    self.shell("sudo mv /tmp{0}.tmp {0}".format(etchosts_path))
    self.shell("sudo chown root:root {0}".format(etchosts_path))

  def update_inventory_group_vars_all(self):
    self.log_task("Update inventory/group_vars/all.yml")

    fo = open("{0}/group_vars/all.yml".format(self.ginas_inventory_path), "a+")
    fo.write("---\n")
    fo.write("users_default_shell: '/bin/bash'\n\n")
    fo.write("apt_debian_http_mirror: 'ftp.us.debian.org'\n")
    fo.write("lxc_template_debootstrap_mirror: 'http://{{ apt_debian_http_mirror }}/debian'\n\n")
    fo.write("console_locales: ['en_US.UTF-8']")
    fo.close()

  def update_inventory_host_vars_machine(self):
    self.log_task("Update inventory/host_vars/{0}.yml".format(self.hostname))

    fo = open("{0}/host_vars/{1}.yml".format(self.ginas_inventory_path, self.hostname), "a+")
    fo.write("---\n")
    if options.apthostpackages:
      packages = self.options.apthostpackages.split()
      fo.write("apt_host_packages: {0}".format(packages))
    fo.close()

  def update_inventory_hosts(self):
    self.log_task("Update inventory/hosts")

    hosts_path = "{0}/hosts".format(self.ginas_inventory_path)

    fo = open(hosts_path, "a+")
    fo.write("localhost ansible_connection=local\n\n")
    fo.write("[workstation]\n")
    fo.write("{0} ansible_connection=local".format(self.hostname))
    fo.close()

  def success_message(self):
    print
    self.log_with_color(36, "Everything has been installed successfully, please check out your inventory:")
    self.log_with_color(35, "cd {0}\n".format(self.ginas_inventory_path))
    self.log_with_color(36, "Visit the getting started guide to setup your first container:")
    self.log_with_color(35, "https://github.com/ginas/ginas/blob/master/docs/getting-started-with-ginas.rst#run-the-common-playbook")

  def log_task(self, task_name):
    self.log_with_color(33, task_name)

  def log_error(self, error_message):
    self.log_with_color(31, error_message)

  def log_with_color(self, color, message):
    print "\033[0;{0}m{1}\033[0m".format(color, message)

  def shell(self, command):
    subprocess.call(command.split(), shell=False)

cli = CLI(options, args)

cli.install_default_apt_packages()
cli.install_ginas()
cli.install_ansible()
cli.update_etc_hosts()
cli.update_inventory_group_vars_all()
cli.update_inventory_host_vars_machine()
cli.update_inventory_hosts()
cli.success_message()

