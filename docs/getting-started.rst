Getting started
===============

.. contents:: Sections
   :local:

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
