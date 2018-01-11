The Site playbook
=================

The :file:`/.local/share/debops/debops/ansible/playbooks/site.yml` connects all
debops roles.

Include own roles/playbooks
---------------------------

If you created a DebOps project directory and added your own role inside
:file:`ansible/roles/` and the playbook file inside :file:`ansible/playbooks/`
you can override the site.yml and hook your role up into DebOps:

:file:`ansible/playbooks/site.yml`

.. code-block:: console

    ---
    - include: '{{ lookup("ENV", "HOME") + "/.local/share/debops/debops/ansible/playbooks/site.yml" }}'
    - include: your_role.yml

:file:`ansible/playbooks/your_role.yml`

.. code-block:: console

    - name: Manage the your specific setup
      hosts: [ 'debops_all_hosts' ]
      roles:

         - role: ansible.your_role
           tags: [ 'role::your_role' ]

Note that :file:`'{{ lookup("ENV", "HOME") + "/.local/share/debops/debops/ansible/playbooks/site.yml" }}'`
only works on Linux. For other systems you can work with a symlink to the
correct destination.
