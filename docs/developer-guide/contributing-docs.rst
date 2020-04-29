.. Copyright (C) 2019 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _contributing_docs:

Contributing to the Documentation
=================================

| Did you just have to trawl through source code to find out what something does?
| Did you have to ask someone on IRC?
| Have you just proudly accomplished your task despite the documentation's lack of relevant information?

Well, help us improve it!

Overview
--------

DebOps' documentation is written in `reStructuredText`__,
built with `Sphinx`__, hosted on readthedocs
and lives in the ``docs/`` folder of the `monorepo`__.

.. __: http://docutils.sourceforge.net/rst.html
.. __: https://www.sphinx-doc.org/
.. __: https://github.com/debops/debops/tree/master/docs

You can build the documentation yourself on
:ref:`your local fork<contribution_workflow>` by running
:ref:`make docs<cmd_make_docs>` from your project folder.


Role documentation
------------------

The documentation for roles lives in ``doc/ansible/roles/``.

The main entry points for role documentation are:

- ``index.rst`` generates the top-level pages for the html documentation
- ``man_index.rst`` generate the role manpages

To keep things uniform, sections go in the following order:

- ``getting_started.rst`` covers initial configuration and basic usage
- *Guides*, *examples* and anything else specific to the role's responsibilities
- ``dependent.rst`` describes usage as a dependent role
- *Default Variables* gets populated from inline markup in roles' ``defaults/main.yml``
- ``defaults-detailed.rst`` contains details for complex variables
- ``defaults-*.rst``, for roles with different types of complex variables
- ``ldap-dit.rst`` describes the LDAP Directory Information Tree a role utilizes

The **manpages** follow the same order, however ``defaults/main`` and
``ldap-dit`` are omitted. They also have their own special files:

Before eveything else:

- ``man_synopsis.rst`` provides a short hint for command line usage
- ``man_description.rst`` provides a description of the role.
  This also gets included at the top of ``index.rst`` when rendering the html.

After everything else:

- ``man_seealso.rst`` mentions any other relevant manpages or links.

Of course, due to DebOps' wide variety of roles, their documentation can also
vary greatly. Plenty of roles are just fine with just a ``getting_started``,
``defaults/main``, and the introductory ``man_`` stuff.


Fixing broken links
-------------------

While working with the documentation, the :ref:`make links<cmd_make_links>`
command can be used to spot and fix broken external links.

- Broken links should be corrected or omitted
- Permanent redirects should be pointed to the new addresses
- Temporary redirects are fine and the listed links are usually desirable


Migration artifacts
-------------------

Due to how the DebOps project was structured during earlier days of developent,
the practice was to ``.. include::`` an :file:`../includes/global.rst` to
share references between multiple git repositories.

The current best practice is to use dynamically generated references,
so if you are editing a file in the documentation and you spot this ``include``,
feel free to remove it and fix the page so it builds without it.


Documentation suggestions
-------------------------

These are a few subjects the current documentation is lacking.

User Manual
~~~~~~~~~~~

- **Debugging tips**: How to find and fix bugs in DebOps

Admin Recipes
~~~~~~~~~~~~~

- **Host Preparation**: Describe how DebOps hosts should be prepared (bootstrapped) for management
- **Common Configuration**: Describe default configuration applied on hosts by the common playbook
- **Basic virtualization**: Describe virtualization on a basic level with LXC, libvirt+KVM
- **Basic mail server**: Describe mail server setup with Postfix, Dovecot
- **Development network**: Describe Vagrant replacement, a development network with DNS, DHCP, PXE and preseeding

Developer Guide
~~~~~~~~~~~~~~~

- **Monorepo layout**: How the DebOps github monorepo is structured
- **Code standards**: How to write Ansible roles for DebOps
- **Software sources**: How DebOps handles external software
- **Project roadmap**: Long term plans for DebOps
- **GitLab CI tests**: How DebOps is tested on GitLab CI
- **Vagrant documentation**: Information about Vagrant usage in tests
- **Jane documentation**: Information about Jane
- **Testinfra documentation**: Information about testinfra usage
