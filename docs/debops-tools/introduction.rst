Introduction
============

The DebOps project consists of a few independent components, which together
allow you to manage a Debian or Ubuntu based server environment. The goal of
the project is to allow easy configuration of a set of Debian servers which can
securely talk to each other and provide various services to other hosts.


Ansible roles
-------------

A set of `Ansible <https://ansible.com/>`_ roles is the main component of the
project. These roles, available both through `Ansible Galaxy <https://galaxy.ansible.com/>`_
and on `DebOps GitHub organization <https://github.com/debops/>`_ can be used
to manage various components of an operating system and applications. The roles
are designed to be used together as "role dependencies" to facilitate automated
configuration of different components - for example a webserver role can tell
the firewall role to open certain ports for specific networks, or an
application role can tell a webserver role to configure a webservice on
specific address.

Most of the provided roles can be used separately in a customized Ansible
playbook if the user wants to use different components for certain services.
The roles can be installed using the :command:`ansible-galaxy` application
without the need to configure the whole DebOps environment. However this use is
meant for advanced users only, and use of the provided playbooks is encouraged.


Ansible playbooks
-----------------

The `debops-playbooks <https://github.com/debops/debops-playbooks>`_ repository
contains a set of Ansible playbooks designed to use the DebOps roles, along
with some custom Ansible plugins and modules useable by different roles. The
goal of the playbooks provided by the project is to create a base environment
on all of the involved hosts using a "common" playbook, and then allow
installation of various services (databases, webservers, etc.) on specific
hosts.

The playbooks define the dependencies used by the roles to for example
let a webserver role configure the firewall with minimal involvement of the
system administrator.

The roles and playbooks are designed in such a way to not require modifications
by the user to make changes. All of the role variables can be modified through
Ansible inventory; configuration passed between the roles can be modified as
well if the environment calls for a more advanced configuration.


DebOps scripts
--------------

A set of Python scripts included in the `debops-tools <https://github.com/debops/debops-tools>`_
GitHub repository, also available via `PyPI <https://pypi.python.org/pypi/debops>`_
provide a simple way to install and update the DebOps roles and playbooks in
a central location. The scripts can be used to create multiple "DebOps project
directories" which can contain separate Ansible inventories, custom playbooks
and roles.

A :command:`debops` script included in the package is used as a wrapper for the
:command:`ansible-playbook` command to facilitate easy execution of the provided
roles and playbooks in different environments.

The optional :command:`debops-padlock` script can be used to create an
encrypted directory backed by `EncFS <https://en.wikipedia.org/wiki/EncFS>`_ and
secured using a `GPG <https://gnupg.org/>`_ key to allow for secure storage of
passwords and other sensitive data.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
