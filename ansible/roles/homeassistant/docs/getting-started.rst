.. Copyright (C) 2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _homeassistant__ref_getting_started:

Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

To setup and manage Home Assistant on a given host or set of hosts, they need to
be added one of the ``[debops_service_homeassistant.*]`` Ansible groups in the
inventory depending on your way of deployment:

.. code:: ini

   [debops_service_homeassistant_nginx]
   hostname

Example playbook
----------------

Ansible playbook that uses the ``debops-contrib.homeassistant`` role and does not
setup a reverse proxy:

.. literalinclude:: playbooks/homeassistant-plain.yml
   :language: yaml
   :lines: 1,5-

Ansible playbook that uses the ``debops-contrib.homeassistant`` role together
with debops.nginx_ as reverse proxy:

.. literalinclude:: playbooks/homeassistant-nginx.yml
   :language: yaml
   :lines: 1,5-

These playbooks are shipped with this role under
:file:`./docs/playbooks/` from which you can symlink them to your
playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider using the
`DebOps Contrib playbooks`_.

Hosting static files
--------------------

`Home Assistant supports hosting static files`__. The role configures the
webserver to serve those files directly. Same as Home Assistant, no
authentication for static files is provided!

To avoid the risk of giving the webserver access the configuration directory
under which the :file:`www` directory is normally stored, the role creates the
:file:`www` directory one level above the configuration directory and creates a
symlink where Home Assistant would read them to not break the application in
any way.

.. __: https://www.home-assistant.io/integrations/http/#hosting-files

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::homeassistant``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::homeassistant:pkgs``
  Tasks related to system package management like installing or
  removing packages.
