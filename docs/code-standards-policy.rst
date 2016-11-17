.. _debops_policy__code_standards_policy:

DebOps Code Standards Policy
============================

.. include:: includes/all.rst

:Date drafted: 2016-11-05
:Date effective: 2017-01-01
:Last changed: 2016-11-17
:Version: 0.1.0
:Authors: - drybjed_
          - ypid_
          - ganto_

.. This version may not correspond directly to the debops-policy version.


.. _debops_policy__ref_code_standards_terminology:

Terminology
-----------

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14, [`RFC2119`_].


.. _debops_policy__ref_code_standards_goals:

Goals of the Policy
-------------------

The DebOps code is comprised of Ansible roles which define data models and
specific tasks that should be performed on hosts to achieve desired results
(installation and configuration of a service or application, interaction with
third-party software and services, etc.), Ansible playbooks which define what
roles should be executed on which hosts, and Ansible inventory which defines
what hosts Ansible should interact with, what playbooks to apply to these hosts
and what parameters to use in the roles.

This Policy describes how the Ansible roles and playbooks should be written,
what ways can be used to combine two or more roles together and how the roles
should be documented.


.. _debops_policy__ref_code_standards_summary:

Summary
-------

**Ansible role: defaults**

- Follow the :ref:`variable naming conventions <debops_policy__ref_code_standards_default_variable_naming_convention>`.

- Make :ref:`conditional code configurable <_debops_policy__ref_code_standards_task_conditions>`
  via default variables.

- :ref:`Comment and structure <debops_policy__ref_code_standards_default_variable_documentation>`
  default variables with reStructuredText.

- Roles providing features for other roles to use MUST do so by offering
  dedicated :ref:`dependent variables <debops_policy__ref_code_standards_dependent_variables>`.


**Ansible role: tasks**

- Make sure the task execution is idempotent.

- :ref:`Describe each task and include <debops_policy__ref_code_standards_task_description>`
  with the ``name`` option.

- Use native :ref:`YAML syntax <debops_policy__ref_code_standards_task_yaml_syntax`
  for task definition formatting.

- If some tasks should only be executed under certain circumstances, group them
  together and conditionally include the task list.

- Set a minimal Ansible version in :file:`meta/main.yml` according to the
  modules and task parameters used.

- :ref:`Disable debug mechanisms <debops_policy__ref_code_standards_task_disable_debug`
  such as the ``debug`` or ``ignore_errors`` statements in the ``master``
  branch.


**Ansible role: templates**

- If possible follow the directory structure of the target file when storing
  the Jinja2 template.

- Properly indent Jinja2 loop constructs.


**Ansible role: dependencies**

- Define role dependencies as :ref:`"soft" dependencies <debops_policy__ref_code_standards_soft_dependencies>`
  via playbook and make them conditional if possible.

- Avoid the use of :ref:`"hard" role dependencies <debops_policy__ref_code_standards_hard_role_dependencies>`
  specified in :file:`meta/main.yml`.

- Don't directly include variables of other roles. Instead use Ansible facts
  to pass configuration state from one role to another.

- Provide dedicated inventory variables if the role configuration is meant to
  be extended by dependent roles.



Ansible role overview
---------------------

Ansible roles are the basic building block of DebOps infrastructure. Due to the
constraints put on them by the DebOps project, they need to be written in
a certain way as to maximize to user's ability to use them through the Ansible
inventory without a requirement to modify the role's code as well as offer the
most amount of reusability so that other Ansible roles can utilize them if
necessary.

Here's the basic set of principles to be aware while writing roles:

- try, if possible, to allow Ansible inventory structure to affect the role
  operation. This means that the role SHOULD allow to use different inventory
  levels to control what data is being used to perform operations. For example,
  if a role manages user accounts, try to support list of accounts from
  ``[all]`` inventory group, from a specific inventory group, and list specific
  to a certain host. However this rule shouldn't be enforced all the time - try
  to use your best judgment of what data should be composable from multiple
  levels of the inventory and which data doesn't need to be.

- each role SHOULD focus on a specific service or application. Roles can be
  composed together inside playbooks if needed, so there's no need to put
  different services together in the same role.
  A exception here are very similar services like the different NTP daemons.
  This has the advantage to only having one set of default variables regardless
  of the particular chosen service and it makes changing the particular service
  every easy.

- roles SHOULD use Ansible local facts stored on the hosts to keep their
  internal state consistent and idempotent at all times, no matter if the role
  is used standalone or a part of another role's playbook. The facts can be
  either static or dynamically generated, or a combination of the two.

- variables from other roles MUST NOT be used directly in your role. This impedes the
  portability of a role and effectively makes the other roles it uses its hard
  dependencies. Instead, roles SHOULD expose the external data structures as
  needed for other roles to use as Ansible local facts; this should ensure that the
  data used by other roles is available at all times, and therefore idempotent.



.. _debops_policy__ref_code_standards_role_default_variables:

Ansible role default variables
------------------------------

.. _debops_policy__ref_code_standards_default_variable_naming_convention:

Naming convention
~~~~~~~~~~~~~~~~~

DebOps roles MUST use a special variable naming scheme to indicate
a "namespace" of a given role default variables. The variable MUST contain
the role name, followed by two underscore characters, followed by the rest of
the variable name. For example, the variable which defines the name of the
:command:`nginx` UNIX user account MUST be defined as (or similar):

.. code-block:: yaml

   nginx__user: 'www-data'

For another example, the list of APT packages to install on a particular host
using the debops.apt_install_ role MUST be defined as (or similar):

.. code-block:: yaml

   apt_install__host_packages: [ 'bash' ]

Variables which are meant to be
:ref:`dependent variables <debops_policy__ref_code_standards_dependent_variables>`
on a provider role, MUST additionally contain the word ``dependent`` in their
variable name. E.g.:

.. code-block:: yaml

   apt_preferences__dependent_list: []

Variables which are meant to define dependent variables in the consumer role
are named after the dependent variable of the provider role prefixed with the
consume role name. E.g.

.. code-block:: yaml

   nginx__apt_preferences__dependent_list:
     - package: 'nginx nginx-*'
       backports: [ 'wheezy', 'precise' ]


.. _debops_policy__ref_code_standards_default_variable_documentation:

Variable documentation
~~~~~~~~~~~~~~~~~~~~~~

For each role the `DebOps Documentation`_ is will include a page which
documents the default variables. This page is generated from the role's
:file:`defaults/main.yml` file with help of yaml2rst_. The entire comment of
the defauls file is thereby interpreted as reStructuredText_ and then rendered
via Sphinx_.

Each variable comment is started with a ``.. envvar::`` reference anchor
followed by the name of the variable. This construct allows any documentation
page to reference the variable via ``:envvar:`varname``` which :program:`Sphinx`
will translate into a link pointing to the variable description. Below the
anchor a comment should describe the purpose of the variable, accepted values,
side effects and so on. Within the comment all reStructuredText constructs
supported by :program:`Sphinx` can be used. An example variable definition would
eventually look like this:

.. code-block:: yaml

    # .. envvar:: ferm__flush [[[
    #
    # Should ferm-rules be flushed when :program:`ferm` is disabled? The default is true,
    # but you may need set both :envvar:`ferm__enabled` and this to ``False`` if you are
    # running in some container and are not allowed to change :command:`iptables`.
    ferm__flush: '{{ ferm__enabled | bool }}'
                                                                   # ]]]

Related default variables should be grouped to sections for a better overview
and easier navigation. For example it makes sense to distinguish packaging and
network related variables. Of course additional or different section titles
might be meaningful for the individual role:

.. code-block:: yaml

    # APT packages [[[
    # ----------------

    [... packaging related variables ...]

                                                                   # ]]]
    # Network configuration [[[
    # -------------------------

    [... networking related variables ...]
                                                                   # ]]]

.. _debops_policy__ref_code_standards_dependent_variables:

Dependent variables
-------------------

DebOps is designed in a way that there are divided responsibilities between the
roles. Each role has its clear task to fulfill. For example an application role
must never care about the firewall configuration by itself. There is a dedicated
role for firewall configuration. And the application role needs a way to tell
the firewall role which access rules to configure. This is done via dependent
variables.

Each role providing a feature which MAY be consumed by other roles MUST provide
a dedicated dependent variable for the configuration of this feature. As that
variable is always defined in the context of the consuming role, its value MUST
NOT modify a shared configuration state (e.g. configuration template). The
provider role might be executed multiple times depending on the role dependency
configuration of the consuming roles.

.. caution::

   A role providing dependent variables MUST be able to handle multiple
   role executions with different values of the dependent variables without
   mutual interference.

Ideally the dependent variable SHOULD accept a list of YAML dictionaries
where one property MUST be the state (``present`` or ``absent``) of the
configuration. The provider role SHOULD then manage an individual configuration
file per list item which allows it to selectively add or remove configuration
states.

**Example:**

The debops.apt_preferences_ role is implements a feature to set APT package
pinning configurations. Each role requiring a specific version of a package
to be available can as the ``apt_preferences`` to do the corresponding
configuration. For this, ``apt_preferences`` provides the following dependent
variable:

.. code-block:: yaml

   # List of :manpage:`apt_preferences(5)` pins to configure in
   # :file:`/etc/apt/preferences.d/`.  This variable is meant to be used from a
   # role dependency in :file:`role/meta/main.yml` or in a playbook.
   apt_preferences__dependent_list: []

The consumer role, in this case debops.nginx_ would then define an own variable
which defines the necessary pinning information:

.. code-block:: yaml

   nginx__apt_preferences__dependent_list:
     - package: 'nginx nginx-*'
       backports: [ 'wheezy', 'precise' ]

In the playbook a :ref:`soft dependency <debops_policy__ref_code_standards_soft_role_dependencies>`
can be specified where the dependent variable is passed to the provider:

.. code-block:: yaml

   - name: Manage nginx webserver
     hosts: 'debops_service_nginx'
     become: True

     roles:

       - role: debops.apt_preferences
         apt_preferences__dependent_list:
           - '{{ nginx__apt_preferences__dependent_list }}'

       - role: debops.nginx

By including the configuration for the debops.apt_preferences_ role in the
``nginx`` default variables the user to change it through the Ansible inventory
without the need to modify any of the involved roles or the playbook.


.. _debops_policy__ref_code_standards_role_tasks:

Ansible role tasks
------------------

Ansible tasks are doing the actual work namely querying and modifiying the
target host. Each task defines a `Ansible Module <https://docs.ansible.com/ansible/modules.html>`_
invocation with a number of general and module specific options.

.. _debops_policy__ref_code_standards_task_description:

Description
~~~~~~~~~~~

Each task MUST have the ``name`` option set with a meaningful description. This
allows to quickly reason about the change impact when running a playbook and
classify the progress in case of an abortion.

**Example:**

.. code-block:: yaml

    - name: Check if password history database exists
      stat:
        path: '/etc/security/opasswd'
      register: auth__register_opasswd

The same is true for the ``include`` statement. Especially for conditional
includes which may be skipped it's helpful for identifying which features of
the role have been left out.

**Example:**

.. code-block:: yaml

    - name: Configure acme-tiny support
      include: acme_tiny.yml
      when: (pki__enabled|bool and
             (pki__acme|bool or pki__acme_install|bool))

.. _debops_policy__ref_code_standards_task_conditions:

Conditions
~~~~~~~~~~

It might be necessary often that task execution might depend on a certain
condition using the ``when`` statement. In many cases the condition is simple
and straight forward, for example when depending on the existance of a file.
Other times the condition might be more complex, for example when depending
on a state of other role configurations. In this case the expression SHOULD
be defined in a default variable. This would give the user the ability to
override the decision and have better control about the role's behavior.

**Example:**

.. code-block:: yaml

    - name: Add database server user to specified groups
      user:
        name: 'mysql'
        groups: '{{ mariadb_server__append_groups | join(",") | default(omit) }}'
        append: True
        createhome: False
      when: mariadb_server__pki|bool

Here the condition ``mariadb_server__pki`` is a extensive evaluation of the
current state. The related default variable is defined in
:file:`defaults/main.yml` as following:

.. code-block:: yaml

    # Enable or disable support for SSL in MariaDB (using ``debops.pki``).
    mariadb_server__pki: '{{ (True
                          if (ansible_local|d() and ansible_local.pki|d() and
                              ansible_local.pki.enabled|d() and
                              mariadb_server__pki_realm in ansible_local.pki.known_realms)
                          else False) | bool }}'

If the user doesn't agree with the defined condition, the variable can simply
be redefined in the Ansible inventory without the need to modify the Ansible
code of the role.

.. _debops_policy__ref_code_standards_task_yaml_syntax:

YAML syntax
~~~~~~~~~~~

Task definitions MUST use the native YAML syntax formatting. Ansible accepts
various ways to define Ansible tasks. However, there are several advantages by
agreening on the YAML syntax:

- Unified coding style

- Vertical formatting is easier to read

- Supports complex parameter values (e.g. nested dictionaries)

**Example:**

Instead of ...

.. code-block:: yaml

   - name: Create plugin path
     file: path={{ elasticsearch__path_plugins }} state=directory

... use the correct YAML syntax:

.. code-block:: yaml

   - name: Create plugin path
     file:
       path: '{{ elasticsearch__path_plugins }}'
       state: directory

.. _debops_policy__ref_code_standards_task_disable_debug:

Disable debug statements
------------------------

Role authors MUST NOT unconditionally use Ansible debug mechanisms such as the
``debug`` module or the ``ignore_errors`` task statement in code which is used
for normal operations. Released code is expected to be functional under every
possible circumstance otherwise it is considered to be a bug which must be
fixed on a best effort basis.

For fragile or complex code paths it might be acceptable to to use the
``debug`` statement with an increased ``verbosity`` level. This will only show
the message, if :program:`ansible-playbook` is executed with one or more
``--verbose`` options. For example:

.. code-block:: yaml

   - name: Show intermediate value from a lookup query
     debug:
       var: '{{ lookup("template", "lookups/fancy_lookup.j2") }}'
       verbosity: 1


.. _debops_policy__ref_code_standards_role_dependencies:

Ansible role dependencies
-------------------------

.. _debops_policy__ref_code_standards_soft_role_dependencies:

Soft role dependencies
~~~~~~~~~~~~~~~~~~~~~~

Role dependencies are considered "soft" if they are defined in the ``roles``
list of a playbook. This approach offers a higher flexibility as the user can
choose which playbooks to run and which features to include.

Whenever possible DebOps role authors MUST specify role dependencies via
playbook instead of
:ref:`"hard" dependencies <debops_policy__ref_code_standards_hard_role_dependencies>`
in the :file:`meta/main.yml`.

It's also possible to pass configuration values to a dependent role if the
involved role is offering dedicated
:ref:`dependent variables <debops_policy__ref_code_standards_dependent_variables>`
for this purpose. With soft dependencies custom playbook authors are therefore
free to pass values from arbitrary sources according to their requirements.

**Example:**

This is an example playbook for debops.slapd_ defining soft dependencies:

.. code-block:: yaml

    ---

    - name: Manage OpenLDAP service
      hosts: [ 'debops_service_slapd', 'debops_slapd' ]
      become: True

      roles:

        - role: debops.ferm
          tags: [ 'role::ferm' ]
          ferm__dependent_rules:
            - '{{ slapd_ferm_dependent_rules }}'

        - role: debops.tcpwrappers
          tags: [ 'role::tcpwrappers' ]
          tcpwrappers_dependent_allow:
            - '{{ slapd_tcpwrappers_dependent_allow }}'

        - role: debops.slapd
          tags: [ 'role::slapd' ]


.. _debops_policy__ref_code_standards_hard_role_dependencies:

Hard role dependencies
~~~~~~~~~~~~~~~~~~~~~~

Role dependencies are considered "hard" if they are defined in the
``dependencies`` list in :file:`meta/main.yml`.  DebOps role authors MUST
avoid the use of hard role dependencies for the follwing reasons:

- Hard role dependencies must always be installed on the Ansible controller
  even when their execution is conditionally triggered via ``when`` statement.

- It hinders the independent use of the role in a custom playbook or outside
  of DebOps where playbook authors might relay on a different role for a certain
  feature or decide no to use a certain feature at all.

- The playbook execution flow is more difficult to reason about as hard
  dependencies are defined outside of the playbook.

Generally role dependencies MUST be defined as
:ref:`"soft" dependencies <debops_policy__ref_code_standards_soft_role_dependencies>`
via playbook unless the tight coupling to another role is unavoidable for
implementing the required functionality.
