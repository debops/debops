.. Copyright (C) 2020 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


General role usage
------------------

The role will configure an APT repository provided by the InfluxData
company to allow secure installation of various software packages developed by
said company. The GPG key used by the repository is downloaded from a OpenPGP
keyserver to ensure authenticity and verification by a third party.

The role itself does not install any APT packages by default. The APT package
selection can be performed either using Ansible inventory, or through role
dependent variables.

In an example application role, create a YAML list variable that contains APT
packages you want to install:

.. code-block:: yaml

   application__influxdata__dependent_packages:
     - 'influxdb'
     - 'telegraf'

Then, in either the playbook, or in role dependencies, use that variable with
the ``influxdata`` role to specify what APT packages to install:

.. code-block:: yaml

   roles:

     - role: influxdata
       influxdata__dependent_packages:
         - '{{ application__influxdata__dependent_packages }}'

The role will install selected packages automatically after configuring the
repository. When this mechanism is used, the Ansible local facts that contain
application versions will be correctly updated by the role.


Ansible local facts
-------------------

The ``debops.influxdata`` role provides a set of Ansible local facts which can
be used by other roles. In the ``ansible_local.influxdata.packages`` YAML
dictionary you can find a YAML dictionary which contains all APT package names
recognized by the role as keys, and their installed version as values. You can
use these facts to for example provide an accurate version number on your role
to check against ``version_compare()`` Ansible filter:

.. code-block:: yaml

   application__version: '{{ ansible_local.influxdata.packages.influxdb|d("0.0.0") }}'

You can also use the ``ansible_local.influxdata.packages`` fact to check if
a given InfluxData application is installed:

.. code-block:: yaml

   application__present: '{{ "influxdb" in (ansible_local.influxdata.packages|d({})) }}'


Example inventory
-----------------

To enable configuration of the InfluxData APT repositories, you need to
add a host to the ``[debops_service_influxdata]`` Ansible inventory group:

.. code-block:: none

    [debops_service_influxdata]
    hostname

The role will be automatically used by other Ansible roles that manage
InfluxData software, therefore the above step is not strictly necessary.
Refer to the documentation of these roles for more details.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.influxdata`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/influxdata.yml
   :language: yaml
   :lines: 1,6-
