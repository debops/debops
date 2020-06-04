.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _mailman__ref_mailman2_migration:

Migration from Mailman 2.x to Mailman 3.x
=========================================

.. only:: html

   .. contents::
      :local:


Overview
--------

Before doing the migration, review the `official migration instructions`__ to
get an overview of the procedure.

.. __: https://docs.mailman3.org/en/latest/migration.html

The :ref:`debops.mailman` role does not support installation of Mailman 2.1 and
Mailman 3 on the same host. You should create a new host for the Mailman site
and import the list configuration as well as the list archives from the old
one. Don't remove the old Mailman 2.1 installation just yet, you might need it
to modify the list configuration files in case the import doesn't work. For
example, there are known issues with the ``bounce_info`` configuration not
being parsable by Mailman 3. You can `use the existing Mailman installation`__
to reset these values.

.. __: https://lists.mailman3.org/archives/list/mailman-users@mailman3.org/thread/JEPMB3HW4FI57EUMOST4L7BD2ILIIS3P/


Example migration steps
-----------------------

Here's an example migration procedure of the ``example-list@lists.example.org``
mailing list, based on the Mailman packages distributed in Debian. We assume
that both hosts (old Mailman 2.x installation and new Mailman 3.x installation)
are running and are accessible only from the Ansible Controller, cannot
communicate directly. The procedure can be performed before the Mailman
3 website is available publicly.

Old Mailman 2.1.x host
~~~~~~~~~~~~~~~~~~~~~~

Reset bounce information for a given list:

.. code-block:: console

   # Switch to 'root' account
   sudo -i

   # Reset bounce configuration (repeat for each list)
   echo 'bounce_info = {}' > /tmp/reset_bounceinfo.py
   config_list -i /tmp/reset_bounceinfo.py example-list

   # Create tarball w list configuration and archives
   tar -czvf /tmp/example-list.tar.gz -C /var/lib/mailman \
       lists/example-list/config.pck \
       archives/private/example-list.mbox/example-list.mbox

Ansible Controller
~~~~~~~~~~~~~~~~~~

Copy the tarball between the old Mailman 2.1.x host and new Mailman 3.x host:

.. code-block:: console

   scp -3 old-mailman:/tmp/example-list.tar.gz \
          new-mailman:/tmp/example-list.tar.gz

New Mailman 3.x host
~~~~~~~~~~~~~~~~~~~~

Extract the tarball contents:

.. code-block:: console

   cd /tmp
   tar -zxvf example-list.tar.gz

Create new mailing list and import the old configuration and archives:

.. code-block:: console

   # Switch to 'root' account
   sudo -i

   mailman create example-list@lists.example.org
   mailman import21 example-list@lists.example.org /tmp/lists/example-list/config.pck

   # Import list archives
   /usr/share/mailman3-web/manage.py hyperkitty_import \
       -l example-list@lists.example.org \
       /tmp/archives/private/example-list.mbox/example-list.mbox

   # Refresh archive index
   /usr/share/mailman3-web/manage.py update_index

After these steps, you should be able to see the mailing list information in
the Postorious interface, as well as the mailing list archives in HyperKitty.
