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

The role can automatically enable Java support in R, if Java environment
installed by the ``debops.java`` Ansible role is detected. To do that, add the
host to the ``[debops_service_java]`` Ansible inventory group:

.. code-block:: none

   [debops_service_java]
   hostname

   [debops_service_cran]
   hostname

If you already configured R and you want to enable Java support, remove the
:file:`/etc/ansible/facts.d/cran.fact` file from the remote host; this will
tell the role to configure Java support in the R environment on the next
Ansible run.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.cran`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/cran.yml
   :language: yaml
