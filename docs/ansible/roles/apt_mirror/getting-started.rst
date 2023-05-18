.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:


Default configuration
---------------------

The ``apt-mirror`` Debian package creates a simple layout of mirror directories
in :file:`/var/spool/apt-mirror/` directory and uses a single :command:`cron`
job to manage mirroring. The :ref:`debops.apt_mirror` extends this setup with
multiple separate mirror configurations which converge in the same
:file:`/var/spool/apt-mirror/mirror/` directory and use separate
:command:`cron` jobs for each set of mirrored repositories. This allows for
different mirror frequency for specific APT repositories if desired.

The mirrored APT repositories are stored in the
:file:`/var/spool/apt-mirror/mirror/` directory, which will be published using
the :command:`nginx` webserver via the :ref:`debops.nginx` role. Different APT
repositories will be published under subdirectories based on their FQDNs, for
example the Debian APT repository will be published as:

.. code-block:: none

   http://<mirror.host>/deb.debian.org/debian

An example :man:`sources.list(5)` entry can look like:

.. code-block:: none

   deb http://<mirror.host>/deb.debian.org/debian bullseye main contrib non-free

The default :command:`nginx` configuration separates HTTP and HTTPS protocols,
so that the clients can select which protocol they prefer. Users can modify the
:command:`nginx` configuration if they want to enable HTTP Basic Authentication
for the mirror by APT clients.

The APT clients still need to configure the GPG keys for a given mirrored APT
repository separately. This can be done using the :ref:`debops.apt` or
:ref:`debops.keyring` Ansible roles.


Usage behind a HTTP proxy
-------------------------

The :command:`apt-mirror` script uses :command:`wget` behind the scenes to
download files. If the mirror is located behind a HTTP proxy,
:file:`/var/spool/apt-mirror/.wgetrc` configuration file with proxy
configuration can be used to access the HTTP proxy - it should work both on the
command line as well as via the :command:`cron` job.


Example inventory
-----------------

To install and configure :command:`apt-mirror` on a given host, it should be
included in a specific Ansible inventory group:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_apt_mirror]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.apt_mirror`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/apt_mirror.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::apt_mirror``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
