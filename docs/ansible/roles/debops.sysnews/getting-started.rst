Getting started
===============

.. contents::
   :local:


How to add news manually
------------------------

The System News entries added by this role using ``sysnews__*_entries``
variables are permanent, ie. they will not expire automatically after a month.

System administrators can add more temporary news entries by putting text files
in the :file:`/var/lib/sysnews/` directory, with the filename being the title
of a news item. This directory is owned by the ``staff`` UNIX system group, and
any users in this group can also add entries in that directory. Custom news
entries will be automatically removed after a month.

To make temporary news items permanent, you can edit the
:file:`/var/lib/sysnews/.noexpire` file. Put names of the custom files to
retain outside of the ``ANSIBLE MANAGED BLOCK`` section, this way your custom
changes will be preserved during the next Ansible run of this role.


Example inventory
-----------------

The ``debops.sysnews`` role can be enabled on a host when it's added to
a particular Ansible inventory group:

.. code-block:: none

   [debops_service_sysnews]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.sysnews`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/sysnews.yml
   :language: yaml
