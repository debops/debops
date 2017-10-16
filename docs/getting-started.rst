Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

Contrary to usual DebOps practice, upstream APT repositories configured by the
``debops.cran`` role are enabled by default, due to `incompatibilities between Debian Stable package versions and packages provided by CRAN <https://cran.r-project.org/bin/linux/debian/#debian-stretch-stable>`_.
The users are still able to disable upstream APT repositories and use the R APT
packages provided by their OS release if they wish, before configuring the
R environment.


Example inventory
-----------------

To configure the R environment on a host, it needs to be included in the
``[debops_service_cran]`` Ansible inventory group:

.. code-block:: none

   [debops_service_cran]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.cran`` role:

.. literalinclude:: playbooks/cran.yml
   :language: yaml
