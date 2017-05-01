Getting started
===============

.. contents:: Sections
   :local:

.. include:: includes/all.rst

Support for backported Java versions
------------------------------------

The role will install OpenJDK 8 environment on Debian Jessie by default, using
the backported packages from the ``jessie-backports`` repository. Backports are
configured using debops.apt_ Ansible role; if the ``debops.java`` does not
detect the debops.apt_ configuration, it will switch to the default JRE
packages available for a given release. Remember to use the provided example
playbook, which will configure APT preferences for the ``ca-certificates-java``
package.


Support for Oracle Java packages
--------------------------------

To use the non-free Oracle Java packages, check the `JavaPackage <https://wiki.debian.org/JavaPackage>`_
page on Debian Wiki to see how to build the proper APT packages with non-free
Java. You will need to publish them in a local APT repository. After that, you
can change the default Java package in ``java__base_packages`` list to your
preferred version.


Example inventory
-----------------

To configure a Java environment on a specific host, it needs to be added to the
``[debops_service_java]`` host group in Ansible inventory:

.. code-block:: none

   [debops_service_java]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.java`` role:

.. literalinclude:: playbooks/java.yml
   :language: yaml
