#! /usr/bin/env python

import platform
import os
import subprocess
import socket
from optparse import OptionParser

VERSION = "0.1.0"
SUPPORTED_PLATFORMS = ["debian", "Ubuntu"]

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

(options, args) = parser.parse_args()

class CLI:
  def __init__(self, options, args):
    self.options = options
    self.args = args

    self.hostname = socket.gethostname()

    if self.options.installpath is None:
      self.log_error("You must supply an installation path, example: -i /tmp/foo")
      quit()

    self.ginas_install_path = os.path.join(self.options.installpath, "ginas")
    self.ginas_inventory_path = os.path.join(self.ginas_install_path, "inventory")

    if os.path.exists(self.ginas_install_path):
      self.log_error("Ginas has already been installed to: {0}".format(self.ginas_install_path))
      quit()

  def exit_if_unsupported_os(self):
    os_platform = platform.linux_distribution()[0]

    for p in SUPPORTED_PLATFORMS:
      if os_platform == p:
        return

    self.log_error("Sorry your OS ({0}) is not supported at this time".format(os_platform))
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
    proc = subprocess.Popen(["ansible --version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    (out, err) = proc.communicate()

    if ('ansible: not found' in out or self.options.forceinstallansible):
      self.log_task("Install ansible:")
      self.shell("{0}/contrib/bootstrap-ansible.sh".format(self.ginas_install_path))

  def check_fqdn(self):
    etchosts_path = "/etc/hosts"
    etchosts_temp_path = "/tmp{0}.tmp".format(etchosts_path)

    proc = subprocess.Popen(["hostname -f"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    if "." in out and out[:-1] in open(etchosts_path).read():
      return

    fqdn = self.get_fqdn_input()

    if len(fqdn) == 0:
      return

    self.log_task("Update {0}".format(etchosts_path))

    self.shell("mkdir -p /tmp{0}".format(etchosts_path))
    self.shell("cp {0} {1}".format(etchosts_path, etchosts_temp_path))

    fo = open(etchosts_temp_path)
    etc_hosts = fo.readlines()
    fo.close()

    localhost = "127.0.0.1"
    localhost_alternative = "127.0.1.1"
    modify_line_index = -1
    replace_line = False
    fqdn_line = "{0} {1} {2}".format(localhost_alternative, fqdn, self.hostname)
    for index, line in enumerate(etc_hosts):
      if line.startswith(localhost_alternative):
        modify_line_index = index
        replace_line = True
        break
      if line.startswith(localhost):
        modify_line_index = index + 1
        break

    if replace_line:
      etc_hosts[modify_line_index] = fqdn_line
    else:
      if modify_line_index > len(etc_hosts):
        etc_hosts.append(fqdn_line)
      else:
        etc_hosts[modify_line_index] = fqdn_line

    fo = open(etchosts_temp_path, "w+")
    for item in etc_hosts:
      fo.write("{0}\n".format(item))
    fo.close()

    self.shell("sudo mv {1} {0}".format(etchosts_path, etchosts_temp_path))
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
    if options.apthostpackages:
      fo.write("---\n")
      packages = self.options.apthostpackages.split()
      fo.write("apt_host_packages: {0}".format(packages))
    fo.close()

  def update_inventory_hosts(self):
    self.log_task("Update inventory/hosts")

    hosts_path = "{0}/hosts".format(self.ginas_inventory_path)

    fo = open(hosts_path, "a+")
    fo.write("# Ansible runs on all hosts from your inventory by default.\n\n")
    fo.write("# In ginas, it is beneficial to have your computer have common tasks ran on it. This gives you postfix, proper dns and wildcard sub-domain support.\n")
    fo.write("# To get the full list of common tasks that will be ran then head over to playbooks/common.yml. Most of them are very light weight.\n\n")
    fo.write("[ansible_controllers]\n")
    fo.write("{0} ansible_connection=local".format(self.hostname))

  def success_message(self):
    print
    self.color_up(36, "Everything has been installed successfully, please check out your inventory:")
    self.color_up(35, "cd {0}\n".format(self.ginas_inventory_path))

    self.color_up(36, "Your computer has been added to an ansible_controllers group in inventory/hosts:")
    self.color_up(35, "Please make sure to check out this file if you do not want this behavior\n")

    self.color_up(36, "Visit the getting started guide to setup your first container:")
    self.color_up(35, "https://github.com/ginas/ginas/blob/master/docs/getting-started-with-ginas.rst#run-the-common-playbook")

  def log_task(self, task_name):
    print self.color_up(33, task_name)

  def log_error(self, error_message):
    print self.color_up(31, error_message)

  def get_fqdn_input(self):
    print
    print self.color_up(31, "A fully qualified domain name (fqdn) was not found in /etc/hosts")
    print
    print "To make dns work properly you must supply a fqdn"
    print "For example: {0} (it needs at least 1 period)".format(self.color_up(33, self.hostname + '.dev'))
    print

    fqdn = ""
    while True:
      fqdn = raw_input(self.color_up(36, "Enter in a fqdn or leave it blank to skip this step: "))

      if len(fqdn) == 0 or "." in fqdn:
        break

    return fqdn

  def color_up(self, color, message):
    return "\033[0;{0}m{1}\033[0m".format(color, message)

  def shell(self, command):
    subprocess.call(command.split(), shell=False)

cli = CLI(options, args)

cli.exit_if_unsupported_os()
cli.install_default_apt_packages()
cli.install_ginas()
cli.install_ansible()
cli.update_inventory_group_vars_all()
cli.update_inventory_host_vars_machine()
cli.update_inventory_hosts()
cli.check_fqdn()
cli.success_message()

