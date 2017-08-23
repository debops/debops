.. _roundcube__ref_upgrade_notes:

Upgrade notes
=============

.. include:: includes/all.rst

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
:ref:`roundcube__ref_changelog` for more details about what has changed.


From v0.1.3 to v.0.2.0
----------------------

Due to changes in the role dependencies and some adjustments in the role's
default values, your setup is likely to break if you simply execute the
updated role. To avoid this, take care of the following issues:

- If you are using a custom playbook, make sure to review the changes in
  :ref:`roundcube__ref_example_playbook`.

- The following variables were replaced and therefore are not defined
  anymore in the default variables:

  - ``roundcube__nginx_server``
  - ``roundcube__nginx_upstream_php5``
  - ``roundcube__php5_packages``
  - ``roundcube__php5_pool``
  - ``roundcube__extra_packages``

  In case your playbook is referencing one of them, make sure they are
  properly defined in your inventory or update your playbook. If you are using
  the example playbook but customized one of those variables in your Ansible
  inventory update the definition accordingly.

- The default installation path defined in :envvar:`roundcube__www` changed.
  If you didn't customize its value the Roundcube installation will be under
  a new file system path after the installation.

**Upgrade procedure**

The following procedure is valid if you are using the role dependencies as
defined in the example playbook.

1. Make sure you have the latest version of the DebOps roles.

   .. code:: shell

      $ debops-update

2. Make sure you have the lastest version of the debops-contrib.roundcube_
   role. In your DebOps project directory run:

   .. code:: shell

      $ ansible-galaxy install --force --no-deps --roles-path=ansible/roles debops-contrib.roundcube

2. Review the :ref:`roundcube__ref_changelog` and make sure your Ansible
   inventory is adjusted to the variable changes (if necessary).

3. Remove the nginx virtual host and PHP definitions created by the
   debops.nginx_ role from the Roundcube server:

   .. code:: shell

      # rm /etc/nginx/{sites-available,sites-enabled}/roundcube.example.com.conf
      # rm /etc/nginx/conf.d/upstream_php5_roundcube.conf

4. Run the role (e.g. via example playbook):

   .. code:: shell

      $ debops ansible/roles/debops-contrib.roundcube/docs/playbooks/roundcube.yml

5. In case you are using the default configuration copy the Roundcube
   SQLite database containing the user settings to the new installation path.

   .. code:: shell

      $ cp /srv/www/roundcube/sites/roundcube.example.com/public/db/roundcube.db \
        /srv/www/sites/roundcube.example.com/public/db

6. In case Roundcube was installed into a new directory but you didn't use the
   default :envvar:`roundcube__www` configuration before the update or you
   experience SQL schema issues, you need to manually run the upstream post
   update script on the Roundcube server. The given ``--version`` parameter
   indicates the previous Roundcube version you were updating from.

   .. code:: shell

      # su roundcube -s /bin/bash \
        -c "php /srv/www/sites/roundcube.example.com/public/bin/update.sh --version=1.1.9"

7. If you manually installed some additional plugins you might need to re-
   install or update them for the new Roundcube version.
