Getting started
===============

.. contents::
   :local:


General role usage
------------------

The role will configure an APT repository provided by the Elastic
company to allow secure installation of various software packages developed by
said company. The GPG key used by the repository is downloaded from a OpenPGP
keyserver to ensure authenticity and verification by a third party.

The role itself does not install any APT packages by default. The APT package
selection can be performed either using Ansible inventory, or through role
dependent variables.

In an example application role, create a YAML list variable that contains APT
packages you want to install:

.. code-block:: yaml

   application__elastic_co__dependent_packages:
     - 'elasticsearch'
     - 'kibana'

Then, in either the playbook, or in role dependencies, use that variable with
the ``debops.elastic_co`` role to specify what APT packages to install:

.. code-block:: yaml

   roles:

     - role: debops.elastic_co
       elastic_co__dependent_packages:
         - '{{ application__elastic_co__dependent_packages }}'

The role will install selected packages automatically after configuring the
repository. When this mechanism is used, the Ansible local facts that contain
application versions will be correctly updated by the role.


Ansible local facts
-------------------

The ``debops.elastic_co`` role provides a set of Ansible local facts which can
be used by other roles. In the ``ansible_local.elastic_co.packages`` YAML
dictionary you can find a YAML dictionary which contains all APT package names
recognized by the role as keys, and their installed version as values. You can
use these facts to for example provide an accurate version number on your role
to check against ``version_compare()`` Ansible filter:

.. code-block:: yaml

   application__version: '{{ ansible_local.elastic_co.packages.elasticsearch
                             if (ansible_local|d() and ansible_local.elastic_co|d() and
                                 ansible_local.elastic_co.packages|d() and
                                 ansible_local.elastic_co.packages.elasticsearch|d())
                             else "0.0.0" }}'

You can also use the ``ansible_local.elastic_co.packages`` fact to check if
a given Elastic application is installed:

.. code-block:: yaml

   application__es_present: '{{ True
                                if (ansible_local|d() and ansible_local.elastic_co|d() and
                                    ansible_local.elastic_co.packages|d() and
                                    "elasticsearch" in ansible_local.elastic_co.packages.keys())
                                else False }}'


.. _elastic_co__ref_heartbeat_override:

Heartbeat package name conflict
-------------------------------

The Elastic APT repositories provide the ``heartbeat`` package, which
installs the `Heartbeat <https://www.elastic.co/products/beats/heartbeat>`__
uptime monitoring application.

The Debian Archive contains the `heartbeat <https://packages.debian.org/search?keywords=heartbeat>`__
package which provides the ``heartbeat`` service which is a part of the
`Linux High-Availability Stack <http://www.linux-ha.org/wiki/Main_Page>`_.

This creates a conflict in the APT package manager database. The Elastic
developers `are aware of the issue <https://github.com/elastic/beats/issues/3765>`_
and are considering a number of options to resolve it. In the meantime,
a proposed solution is to `use APT pinning to change APT preferences <https://github.com/elastic/beats/issues/3765#issuecomment-289924787>`_
so that the ``heartbeat`` package from the Elastic APT repository is
installed instead of the Debian Archive version (which is a completely
different application).

The `research <https://serverfault.com/questions/260152/>`_ performed by one of
the cluster software users suggests that the `corosync <https://corosync.github.io/corosync/>`_
service is a preferred replacement for the ``heartbeat`` service from the HA
Stack. The `Debian HA Cluster HOWTO <https://wiki.debian.org/Debian-HA/ClustersFromScratch>`_
uses the ``corosync`` service as the messaging layer as well.

Due to the above facts the decision was made that the ``debops.elastic_co``
role will configure the APT preferences of the hosts it's executed on to prefer
the ``heartbeat`` package from the Elastic APT repositories, using
APT preferences. The example Ansible playbook contains the necessary code which
uses the :ref:`debops.apt_preferences` role to perform this task. In a case where you
wish to not configure this override, you can disable it by setting the
:envvar:`elastic_co__heartbeat_override` variable to ``False``. This will
affect the list of package versions included in the Ansible local facts.


Example inventory
-----------------

To enable configuration of the Elastic APT repositories, you need to
add a host to the ``[debops_service_elastic_co]`` Ansible inventory group:

.. code-block:: none

    [debops_service_elastic_co]
    hostname

The role will be automatically used by other Ansible roles that manage
Elastic software, therefore the above step is not strictly necessary.
Refer to the documentation of these roles for more details.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.elastic_co`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/elastic_co.yml
   :language: yaml
