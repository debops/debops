Getting started
===============

.. include:: includes/all.rst

By default all you need to do to use the ``debops.secret`` role is to
include it in your common playbook at the beginning:

.. code-block:: yaml

   ---
   - name: Example playbook
     hosts: all
     become: True

     roles:
       - role: debops.secret

That will allow all your roles in this and subsequent plays to access
the ``secret`` variable and use it consistently.

Unfortunately, it doesn't work well when you use Ansible with ``--tags``
parameter, which might omit your common play, thus not setting ``secret*``
variables at all and changing your passwords to empty values, modifying config
files incorrectly, basically not honoring the idempotency principle.

The solution to that problem is to either include ``debops.secret`` role in all
your plays (similar to the one above), or include it as a dependency in roles
that require it:

.. code-block:: yaml

   ---
   dependencies:
     - role: debops.secret

This will ensure that roles utilizing ``secret`` variable will be able to
access it correctly and you don't need to remember to include
``debops.secret`` role in all your playbooks.


Usage examples
--------------

Example password lookup with password written to a variable. You can define
this variable anywhere Ansible variables can be defined, but if you want to
give playbook users the ability to overwrite it in inventory, you should define
it in :file:`role/defaults/main.yml`:

.. code-block:: yaml

   ---
   mariadb__root_password: '{{ lookup("password", secret + "/credentials/" +
                               ansible_fqdn + "/mariadb/root/password length=20") }}'

When this variable is set in :file:`role/defaults/main.yml`, you can easily
overwrite it in your inventory, like this:

.. code-block:: yaml

   ---
   mariadb__root_password: 'correct horse battery staple'

You can also change the password directly in the secret directory, in this case
in ``secret/credentials/hostname/mysql/root/password`` and Ansible should
update the password on the remote server (if the role is written to support
this).

Example file download task from remote host to Ansible controller, stored in
secret directory:

.. code-block:: yaml

   ---
   - name: Download file to secret directory
     fetch:
       src: '/etc/fstab'
       flat: True
       dest: '{{ secret + "/storage/" + ansible_fqdn + "/etc/fstab" }}'

Example file upload task from Ansible Controller to remote host with file from
secret directory:

.. code-block:: yaml

   ---
   - name: Copy file from secret directory
     copy:
       dest: '/etc/fstab'
       owner: 'root'
       group: 'root'
       mode: '0644'
       src: '{{ secret + "/storage/ + ansible_fqdn + "/etc/fstab" }}"
