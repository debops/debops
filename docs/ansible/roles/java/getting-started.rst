Getting started
===============

.. contents:: Sections
   :local:

Support for backported Java versions
------------------------------------

The role will install OpenJDK 8 environment on Debian Jessie by default, using
the backported packages from the ``jessie-backports`` repository. Backports are
configured using :ref:`debops.apt` Ansible role; if the ``debops.java`` does not
detect the :ref:`debops.apt` configuration, it will switch to the default JRE
packages available for a given release. Remember to use the provided example
playbook, which will configure APT preferences for the ``ca-certificates-java``
package.


Support for Oracle Java packages
--------------------------------

To use the non-free Oracle Java packages, check the `JavaPackage <https://wiki.debian.org/JavaPackage>`_
page on Debian Wiki to see how to build the proper APT packages with non-free
Java. You will need to publish them in a local APT repository. After that, you
can change the default Java package in :envvar:`java__base_packages` list to your
preferred version.


Conditional installation of Java Development Kit (JDK)
------------------------------------------------------

Some environments might require a full Java Development Kit to work correctly,
however by default the ``debops.java`` role installs only the Java Runtime
Environment (JRE). To install the full JDK in a compatible version, you can set
the :envvar:`java__install_jdk` boolean variable to ``True``, either via
Ansible inventory variables or via role dependent variables.


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

.. literalinclude:: ../../../../ansible/playbooks/service/java.yml
   :language: yaml
