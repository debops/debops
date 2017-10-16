Changelog
=========

.. include:: includes/all.rst

**debops.elasticsearch**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.

`debops.elasticsearch master`_ - unreleased
-------------------------------------------

.. _debops.elasticsearch master: https://github.com/debops/ansible-elasticsearch/compare/v0.2.1...master


Fixes
~~~~~

- Fix ``discovery.zen.minimum_master_nodes`` calculation for odd number of nodes. [scibi_]


`debops.elasticsearch v0.2.1`_ - 2017-07-14
-------------------------------------------

.. _debops.elasticsearch v0.2.1: https://github.com/debops/ansible-elasticsearch/compare/v0.2.0...v0.2.1

Fixes
~~~~~

- Ensure that list of plugins is correctly flattened. [drybjed_]

- Make sure that plugins with complex names work. [pedroluislopez, drybjed_]


`debops.elasticsearch v0.2.0`_ - 2017-05-13
-------------------------------------------

.. _debops.elasticsearch v0.2.0: https://github.com/debops/ansible-elasticsearch/compare/v0.1.0...v0.2.0

Sponsors
~~~~~~~~

- The ``debops.elasticsearch`` Ansible role rewrite was sponsored by
  `Comp S.A. <https://www.comp.com.pl/en>`_.

Added
~~~~~

- The documentation has been expanded and includes information about usage of
  the role as a dependency, tips about clustering and security of the
  Elasticsearch cluster. [drybjed_]

- Role now supports usage as a role dependency to allow other Ansible roles to
  manage their own custom configuration to the main Elasticsearch configuration
  file idempotently. [drybjed_]

- The role now detects the system RAM size and automatically configures the JVM
  heap size to use ~20%-50% of the system RAM, depending on the size of the
  available RAM. Role tries not to cross the 32 GB boundary as well, in case
  that a host has more than 64 GB of RAM available. [drybjed_]

- Role automatically generates the list and number of eligible master nodes
  based on the hosts included in the Ansible inventory groups. [drybjed_]

- Role now automatically enables or disables clustering depending on the
  configuration of the firewall. If a suitable subnet is configured, clustering
  is automatically enabled. [drybjed_]

Changed
~~~~~~~

- The role is rewritten from the ground up with the upstream version (5.x+) as
  default. The Elasticsearch packages from OS archives are outdated an
  unsupported. [drybjed_]

- All of the role variables have been renamed from ``elasticsearch_*`` to
  ``elasticsearch__*`` to put them in a separate namespace. You will need to
  update your inventory. [drybjed_]

- The main Elasticsearch configuration file is now generated dynamically from
  the YAML variables included in the role defaults. Individual parameters can
  be overwritten via Ansible inventory variables. [drybjed_]

- Old Ansible inventory groups have been renamed to better reflect the
  Elasticsearch 5.x node functions. You will need to update your inventory.
  [drybjed_]

- The Elasticsearch service will now lock the process memory in RAM by default
  to improve performance and avoid swapping. [drybjed_]

- The Elasticsearch service will now automatically listen on all of the private
  IP addresses along with the ``localhost`` interface if the firewall is
  enabled. You still need to specify the CIDR subnets to accept the
  connections from the outside. [drybjed_]

- The Elasticsearch service now listens on specific ports for HTTP and
  transport connections, instead of port ranges. [drybjed_]

Removed
~~~~~~~

- The upstream APT repository configuration and package installation has been
  removed from the role. The ``debops.elastic_co`` role is used as a dependency
  to manage the APT repository and package installation. [drybjed_]

- Hard role dependencies on debops.ferm_, debops.java_ and debops.etc_services_
  Ansible roles have been removed from the ``debops.elasticsearch`` role and
  moved to the example playbook. [drybjed_]

- Support for management of custom Java libraries has been removed. [drybjed_]

- Log-related configuration has been removed and role relies on the default
  configuration provided by the package. It might be re-introduced later if
  needed. [drybjed_]


debops.elasticsearch v0.1.0 - 2016-10-13
----------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
