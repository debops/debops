Getting started
===============

.. contents::
   :local:


By default DokuWiki is installed on a separate system account ``"dokuwiki"``,
in :file:`/srv/www/dokuwiki/` subdirectory and will be accessible on
``https://wiki.<domain>/``. :ref:`debops.nginx` and :ref:`debops.php` roles are used
to configure the required environment.

Example inventory
-----------------

You can install DokuWiki on a host by adding it to
``[debops_service_dokuwiki]`` group in your Ansible inventory::

    [debops_service_dokuwiki]
    hostname

Example playbook
----------------

Here's an example playbook which uses ``debops.dokuwiki`` role to install
DokuWiki:

.. literalinclude:: ../../../../ansible/playbooks/service/dokuwiki.yml
   :language: yaml


Post-install steps
------------------

When Ansible is finished, if you don't use LDAP, you need to finish the
configuration by opening the ``https://wiki.<domain>/install.php`` page. There
you will be able to set the name of your new wiki, superuser account and
password, and other settings.

You can then login to your wiki and configure it using the administrative
interface.

Some of the provided plugins, for example ``CodeMirror``, might not be
installed correctly. In that case, reinstalling them using the admin interface
should be enough to correctly enable them in DokuWiki.

.. _dokuwiki__ref_ldap_support:

LDAP support
------------

If the LDAP environment managed by the :ref:`debops.ldap` role is configured on
a host on which DokuWiki is installed, the :ref:`debops.dokuwiki` role will
automatically integrate with it and configure LDAP authentication. In that
case, use of the ``/install.php`` script might break the installation because
the install script disables all authentication plugins apart from the
``authplain`` plugin, using the :file:`conf/plugins.local.php` configuration
file. You can still do it if you wish, just remember to remove the ``authldap``
entry from the mentioned file afterwards to restore LDAP support.

Alternatively, you can finish installation after logging in using an
administrator account. You will have to define basic set of ACLs using the ACL
manager - for example to make the whole wiki require authentication to read,
you can define an ACL entry for ``@ALL`` to "None", and an ACL entry for
``@USER`` to "Upload", which will give users the broadest set of permissions
without allowing normal users to delete things. The name of the wiki and
license used by the wiki can be set in the Configuration Manager.

The :ref:`debops.dokuwiki` role by default creates a separate LDAP object (via
the :ref:`debops.ldap` role) that contains the definition of user groups used
by DokuWiki. The LDAP object will be a child of the LDAP account object used to
access the LDAP directory. This configuration is meant to allow configuration
of private DokuWiki instances for different groups of users in the LDAP
directory. If you want to instead use the global groups defined in LDAP, you
can change that by setting the :envvar:`dokuwiki__ldap_private_groups` variable
to ``False``.

One LDAP group will be created by default - "DokuWiki Administrators". This is
a ``groupOfNames`` LDAP object that grants the superuser access to the wiki to
people specified using the ``member`` attribute. You can define your own
additional groups in the same manner as long as they are put below the
``ou=Groups`` LDAP object used by the wiki. Inside of the DokuWiki ACL manager,
these groups have to be specified with the ``@`` prefix, for example
``@DokuWiki Administrators``.

By default access to DokuWiki service is limited to user accounts that have the
``authorizedService`` attribute with either ``dokuwiki``, ``web-public`` or
``*`` values. To change the requirements or give access to the service to all
users, you can edit the LDAP user filter used by DokuWiki, specified in the
:envvar:`dokuwiki__ldap_user_filter` variable.

You should also read the :ref:`dokuwiki__ref_ldap_dit` for details about LDAP
objects and directory structure configured by the :ref:`debops.dokuwiki` role.
