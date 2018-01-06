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

When Ansible is finished, you need to finish the configuration by opening the
``https://wiki.<domain>/install.php`` page. There you will be able to set the
name of your new wiki, superuser account and password, and other settings.

You can then login to your wiki and configure it using the administrative
interface.

Some of the provided plugins, for example ``CodeMirror``, might not be
installed correctly. In that case, reinstalling them using the admin interface
should be enough to correctly enable them in DokuWiki.
