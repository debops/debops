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

Terminology
-----------

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14, [`RFC2119`_].

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

Summary
-------

**Ansible role: defaults**

- Follow the :ref:`variable naming conventions <policy__ref_default_variable_naming_convention>`.

- Make conditional code configurable via default variables.

- :ref:`Comment and structure <policy__ref_default_variable_documentation>`
  default variables with reStructuredText.


**Ansible role: tasks**

- Make sure the task execution is idempotent.

- :ref:`Describe each task and include <policy__ref_task_description>` with the
  ``name`` option.

- Use native YAML syntax for task definition.

- If some tasks should only be executed under certain circumstances, group them
  together and conditionally include the task list.

- Set a minimal Ansible version in :file:`meta/main.yml` according to the
  modules and task parameters used.


**Ansible role: templates**

- If possible follow the directory structure of the target file when storing
  the Jinja2 template.

- Properly indent Jinja2 loop constructs.


**Ansible role: dependencies**

- Try to avoid the use of hard dependencies specified in :file:`meta/main.yml`.

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

- try, if possible, to move much of the conditional code to the role's default
  variables (:file:`defaults/main.yml`). This way, the user can affect the role
  operation without the need to modify the role's internal, private code.

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

- a role SHOULD allow for use by other roles through a dependent variable
  mechanism. This way different roles can pass configuration data to other
  services if needed; for example a web server role can request the firewall
  management role to open specific ports when certain conditions are met.

- avoid use of hard dependencies in roles (those defined in the
  :file:`meta/main.yml` file). The roles MUST only use other roles as
  dependencies through the playbook, unless data from a particular roles is
  used internally by another role and without it the operations might result in
  a non-functional role.

- roles SHOULD use Ansible local facts stored on the hosts to keep their
  internal state consistent and idempotent at all times, no matter if the role
  is used standalone or a part of another role's playbook. The facts can be
  either static or dynamically generated, or a combination of the two.

- variables from other roles MUST NOT be used directly in your role. This impedes the
  portability of a role and effectively makes the other roles it uses its hard
  dependencies. Instead, roles SHOULD expose the external data structures as
  needed for other roles to use as Ansible local facts; this should ensure that the
  data used by other roles is available at all times, and therefore idempotent.

- roles MUST NOT use Ansible debug mechanisms such as ``debug`` and
  ``ignore_errors`` modules/module parameters for normal operations. If
  during development or normal operation a role consistently experiences
  issues, they should be fixed or handled conditionally instead of being
  ignored.


Ansible role default variables
------------------------------

.. _policy__ref_default_variable_naming_convention:

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

The namespace separator MUST be used in variables that directly define data
passed to other Ansible roles through role dependent variables.
For example, if
you want to ensure that a given package is installed from the Debian Backports
repository, you can do so using the debops.apt_preferences_ role. To do that,
in your own role create the default variable:

.. code-block:: yaml

   application__apt_preferences__dependent_list:
     - package: 'nginx nginx-*'
       backports: [ 'wheezy', 'precise' ]

Then, in your role's playbook, you can add the debops.apt_preferences_ role as
a dependency and pass a specific configuration to it:

.. code-block:: yaml

   - name: Install the application
     hosts: 'application_hosts'
     become: True

     roles:

       - role: debops.apt_preferences
         apt_preferences__dependent_list:
           - '{{ application__apt_preferences__dependent_list }}'

       - role: application

By including the configuration for the debops.apt_preferences_ role in your role's
default variables you allow the user to change it through the Ansible inventory
without the need to modify any of the involved roles or the playbook.

.. _policy__ref_default_variable_documentation:

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

Ansible role tasks
------------------

Ansible tasks are doing the actual work namely querying and modifiying the
target host. Each task defines a `Ansible Module <https://docs.ansible.com/ansible/modules.html>`_
invocation with a number of general and module specific options.

.. _policy__ref_task_description:

Description
~~~~~~~~~~~

Each task MUST have the ``name`` option set with a meaningful description. This
allows to quickly reason about the change impact when running a playbook and
classify the progress in case of an abortion. Example:

.. code-block:: yaml

    - name: Check if password history database exists
      stat:
        path: '/etc/security/opasswd'
      register: auth__register_opasswd

The same is true for the ``include`` statement. Especially for conditional
includes which may be skipped it's helpful for identifying which features of
the role have been left out. Example:

.. code-block:: yaml

    - name: Configure acme-tiny support
      include: acme_tiny.yml
      when: (pki__enabled|bool and
             (pki__acme|bool or pki__acme_install|bool))

