Getting started
===============

.. contents:: Sections
   :local:


Reading custom facts
--------------------

The ``debops.debops_fact`` role uses two INI files to store the custom facts,
one "public" and readable by every user on the system, and one "private" and
readable only by specific system group (``root`` by default). Contents of the
files are merged into one variable tree. There are three types of facts
managed by the role, stored in different INI sections.

The ``[default]`` section, available through Ansible local facts as
``ansible_local.debops_fact.*``, can be used to store top-level variables. Keep
in mind that some of the variables on this level are reserved for the
``debops.debops_fact`` role itself and shouldn't be modified by other roles.
Both public and private INI files contain this section.

The ``[global]`` section is stored in the public INI file and can be accessed
as ``ansible_local.debops_fact.global.*``.

The ``[secret]`` section is stored in the private INI file with limited access
controlled by UNIX permissions, and can be accessed as
``ansible_local.debops_fact.secret.*``.


Setting custom facts
--------------------

You can use the ``ini_file`` Ansible module to set custom DebOps facts. The
role provides a set of local facts which can be used as the module parameters
to store the variables in the correct files. The values are read as JSON,
therefore you can use ``to_json`` Ansible filter to correctly store more
complex data structures in the INI files. You shouldn't modify the file
ownership or permissions using the module parameters.

Examples
~~~~~~~~

Set a variable in the ``[default]`` section of the public INI file:

.. code-block:: yaml

   - name: Save DebOps facts
     ini_file:
       dest: '{{ ansible_local.debops_fact.public_facts
                 if (ansible_local|d() and ansible_local.debops_fact|d() and
                     ansible_local.debops_fact.public_facts|d())
                 else "/etc/ansible/debops_fact.ini" }}'
       section: '{{ ansible_local.debops_fact.default_section
                    if (ansible_local|d() and ansible_local.debops_fact|d() and
                        ansible_local.debops_fact.default_section|d())
                    else "default" }}'
       option: 'mta'
       value: True
     when: ansible_local|d() and ansible_local.debops_fact|d() and
           ansible_local.debops_fact.enabled|bool

Add your role to list of roles applied on this host:

.. code-block:: yaml

   - name: Save DebOps facts
     ini_file:
       dest: '{{ ansible_local.debops_fact.public_facts
                 if (ansible_local|d() and ansible_local.debops_fact|d() and
                     ansible_local.debops_fact.public_facts|d())
                 else "/etc/ansible/debops_fact.ini" }}'
       section: '{{ ansible_local.debops_fact.public_section
                    if (ansible_local|d() and ansible_local.debops_fact|d() and
                        ansible_local.debops_fact.public_section|d())
                    else "global" }}'
       option: 'applied_roles'
       value: '{{ ((ansible_local.debops_fact.global.applied_roles
                    if (ansible_local|d() and ansible_local.debops_fact|d() and
                        ansible_local.debops_fact.global|d() and
                        ansible_local.debops_fact.global.applied_roles|d())
                    else []) + [ "username.rolename" ]) | unique | to_json }}'
     when: ansible_local|d() and ansible_local.debops_fact|d() and
           ansible_local.debops_fact.enabled|bool


Example inventory
-----------------

The ``debops.debops_fact`` role is included in the :file:`common.yml` DebOps
playbook and doesn't need to be specifically enabled on a host.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.debops_fact`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/debops_fact.yml
   :language: yaml
