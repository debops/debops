Timeline
========

This document is a summary of the DebOps development over time. You can see
most of the project's history in :command:`git` logs, however tracing it might
be confusing due to the split and subsequent merge of the code back together.
Here, we try to explain why that happened.


Summary of the events
---------------------

The project has been initiated by Maciej Delmanowski in October 2013. In
September 2014, after two project name changes, the code contained in one
:command:`git` repository was moved into multiple :command:`git` repositories
published in the `debops`__ organization on GitHub to allow publication of the
roles in the `Ansible Galaxy`__, as well as better usage of Travis CI to test
the codebase.

.. __: https://github.com/debops/
.. __: https://galaxy.ansible.com/debops/

The decision to move the project codebase to the separate :command:`git`
repositories shaped the DebOps project in multiple ways. It enforced the code
separation between different Ansible roles that required development of proper
ways to make them interact with each other and pass the data around. New open
source projects, `ansigenome`__ and `rolespec`__, were created to aid the
DebOps development and maintenance.

.. __: https://github.com/nickjj/ansigenome/
.. __: https://github.com/nickjj/rolespec/

Unfortunately, the growing codebase resulted in quickly rising number of
:command:`git` repositories to maintain, which sapped the available resources
from project development. There were also issues with packaging the DebOps code
and documentation in Debian, as well as no practical way to provide a "stable
release" due to the separate :command:`git` repositories being independently
tagged and developed. Because of that, in August 2017 the project maintainers
decided to merge all of the :command:`git` repositories back into one monorepo
to make the DebOps development easier.

The process was completed over a period of a few months. As the result, the
development model also changed into a more distributed way with multiple forks
of the main repository. First official stable release was published in
May 2019.


2013
----

May 2013
~~~~~~~~

- `Debian 7.0 (wheezy)`__ becomes a Debian Stable release. It was the first
  Debian release supported by DebOps.

.. __: https://www.debian.org/releases/wheezy/

September 2013
~~~~~~~~~~~~~~

- Ansible 1.3 ("Top of the World") is released. This version introduced the
  role default variables, local facts and role dependencies, which became an
  integral part of DebOps later on.

October 2013
~~~~~~~~~~~~

- `Initial commit`__ in the ``ansible-aiua`` :command:`git` repository which
  will eventually become DebOps.

.. __: https://github.com/debops/debops/tree/eb42149555

- Introduction of `randomly generated passwords`__ with the MySQL role. This
  feature will eventually evolve into :ref:`debops.secret` role and will be
  used almost everywhere in DebOps.

.. __: https://github.com/debops/debops/commit/d53b9ce1c

December 2013
~~~~~~~~~~~~~

- The ``ansible-aiua`` project `is renamed to ginas`__. ginas is not a server.

.. __: https://github.com/debops/debops/tree/d231c08367

- Support for `ownCloud deployment`__ is introduced. The role is used as a test
  case for PHP5 support in the project, and eventually will become one of the
  end-user applications provided in DebOps.

.. __: https://github.com/debops/debops/commit/8ad3cff814


2014
----

February 2014
~~~~~~~~~~~~~

- Project gains `support for Vagrant virtual machines`__, used for
  demonstration purposes.

.. __: https://github.com/debops/debops/commit/e9203b42ce

- `Travis CI tests are introduced`__ to find any issues with pull requests
  before merging them. The project gets its own GitHub organization, and new
  development model using forked repositories is introduced.

.. __: https://github.com/debops/debops/commit/3f7a8554f1

- Introduction of `Sphinx-based documentation`__.

.. __: https://github.com/debops/debops/commit/2f25969383

March 2014
~~~~~~~~~~

- Support for `GitLab CE deployment`__ is introduced.
  The :ref:`gitlab <debops.gitlab>` role will be used to test Ruby support and
  as an integration test for other DebOps roles, as well as to provide
  a :command:`git` server for the IT infrastructures managed by DebOps.

.. __: https://github.com/debops/debops/commit/ca568a7dd2

July 2014
~~~~~~~~~

- Introduction of Nick Janetakis as a first major contributor to the project,
  with `first draft of the Getting Started guide`__.

.. __: https://github.com/debops/debops/commit/ca4ccf2cd6

- Nick Janetakis creates `ansigenome`__ project which is meant to ease
  management of multiple Ansible roles.

.. __: https://github.com/nickjj/ansigenome

August 2014
~~~~~~~~~~~

- The ``ginas`` project `is renamed to DebOps project`__. The ``debops.org``
  DNS domain is registered, project gets its own website, mailing list and
  GitHub organization.

.. __: https://github.com/debops/debops/tree/38e968010b

September 2014
~~~~~~~~~~~~~~

- `The last commit in the old DebOps repository`__. The development if this
  repository has been frozen since. It is now included in the DebOps monorepo
  as a separate ``ginas-historical`` branch.

.. __: https://github.com/debops/debops/tree/93d7d444ec

- Nick Janetakis creates `rolespec`__ project which provides a unified test
  environment for separate DebOps roles based on Travis CI.

.. __: https://github.com/nickjj/rolespec/

- `First version of the DebOps install scripts`__ written in Bash, located in
  the ``debops-tools`` repository. They will be used to download all other
  DebOps repositories with playbooks and roles.

.. __: https://github.com/debops/debops/commit/69fd813993

November 2014
~~~~~~~~~~~~~

- Maciej Delmanowski writes the `ipaddr() Ansible filter plugin`__ for usage
  with :ref:`debops.ifupdown` role and others that require IP address
  manipulation. `The plugin is later merged into Ansible Core`__.

.. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_filters_ipaddr.html
.. __: https://github.com/ansible/ansible/commit/7e46554160

December 2014
~~~~~~~~~~~~~

- Hartmut Goebel `rewrites the Bash DebOps scripts in Python`__. They will be
  later `published on PyPI`__ which will become main installation method.

.. __: https://github.com/debops/debops/commit/88e3a8e
.. __: https://pypi.org/project/debops/

- `debops-tools v0.1.0`__ is released. This repository contains various scripts
  that can be used to install or update DebOps roles and playbooks
  :command:`git` repositories, create project directories, and run the
  playbooks.

.. __: https://github.com/debops/debops/tree/221a475b28

2015
----

February 2015
~~~~~~~~~~~~~

- `debops-playbooks v0.1.0`__ is released. This repository holds the DebOps
  playbooks that tie all of the roles together, and was treated as the "main"
  repository of the project when it was split into multiple :command:`git`
  repositories.

.. __: https://github.com/debops/debops/tree/dcf5b350ae

March 2015
~~~~~~~~~~

- `Robert Chady introduces custom Ansible lookup plugins`__ to the project,
  ``file_src``, ``template_src`` and later ``task_src``, which allow usage of
  custom files and templates inside roles without modifications, as well as
  injection of custom Ansible tasks in the roles.

.. __: https://github.com/debops/debops/commit/df5b535188

April 2015
~~~~~~~~~~

- `Debian 8.0 (jessie)`__ becomes a Debian Stable release.

.. __: https://www.debian.org/releases/jessie/

June 2015
~~~~~~~~~

- Introduction of `MariaDB server and client roles`__ to the project. They were
  used to test and develop split client/server role model with support for
  database server on remote hosts, later adopted in other DebOps roles.

.. __: https://github.com/debops/debops/commit/beff199380

September 2015
~~~~~~~~~~~~~~

- After `discussion in the community`__ role dependency model in DebOps is
  redesigned. Most of the role dependencies will be moved from the role
  :file:`meta/main.yml` configuration to the playbook level to allow easy use
  of various DebOps roles independently from each other.

.. __: https://github.com/debops/debops-playbooks/issues/192

October 2015
~~~~~~~~~~~~

- The `debops-contrib`__ GitHub organization is created to host third-party
  DebOps :command:`git` repositories and serve as a staging point for including
  new Ansible role repositories in DebOps.

.. __: https://lists.debops.org/pipermail/debops-users/2015-October/000049.html


2016
----

January 2016
~~~~~~~~~~~~

- `Ansible 2.0 ("Over the Hills and Far Away")`__ is released.

.. __: https://github.com/ansible/ansible/blob/stable-2.0/CHANGELOG.md

March 2016
~~~~~~~~~~

- The DebOps mailing list `is moved to a self-hosted Mailman installation`__
  based on DebOps, to ensure that `the project is "eating its own dog food"`__.

.. __: https://lists.debops.org/pipermail/debops-users/2016-March/000066.html
.. __: https://en.wikipedia.org/wiki/Eating_your_own_dog_food

April 2016
~~~~~~~~~~

- Daniel Sender creates the first iteration of the `debops`__ Debian package.
  Unfortunately, problems with `debops-doc package`__ prevent full inclusion of
  the project in Debian.

.. __: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=819816
.. __: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=820367

July 2016
~~~~~~~~~

- Robin Schneider `creates DebOps entry`__ in the
  `Core Infrastructure Initiative Best Practices`__ program.

.. __: https://bestpractices.coreinfrastructure.org/en/projects/237
.. __: https://bestpractices.coreinfrastructure.org/en


2017
----

June 2017
~~~~~~~~~

- `Debian 9.0 (stretch)`__ becomes a Debian Stable release.

.. __: https://www.debian.org/releases/stretch/

August 2017
~~~~~~~~~~~

- Maciej Delmanowski `proposes merge of all of the project repositories`__ back
  together into one DebOps monorepo. The plan is to resolve all pending pull
  requests in various repositories before merging starts.

.. __: https://lists.debops.org/pipermail/debops-users/2017-August/000078.html

September 2017
~~~~~~~~~~~~~~

- `debops-tools v0.5.0`__ was the last tagged release of the DebOps scripts
  before the repository was merged into the new DebOps monorepo.

.. __: https://github.com/debops/debops/tree/23e8723aab

October 2017
~~~~~~~~~~~~

- `The last commit`__ in the ``debops-playbooks`` :command:`git` repository.
  Later on the repository will be merged into the new DebOps monorepo.

.. __: https://github.com/debops/debops/commit/fb04a87064

- `All of the pending pull requests in DebOps roles are resolved`__ and the
  code from separate :command:`git` repositories is merged into `single monorepo`__,
  which becomes the main development repository.

.. __: https://lists.debops.org/pipermail/debops-users/2017-October/000102.html
.. __: https://github.com/debops/debops

- `debops v0.6.0`__ is released, along with updated scripts that support
  installation of the monorepo by the :command:`debops-update` command. The
  release is fully compatible with older DebOps roles and playbooks. From this
  point on the old and new codebases start to diverge.

.. __: https://github.com/debops/debops/tree/1250d75c91

- `ypid roles from 'debops-contrib' organization are merged`__ to the DebOps
  monorepo without further changes; they will be integrated with the main
  playbook later on.

.. __: https://github.com/debops/debops/tree/1c884c0af4

November 2017
~~~~~~~~~~~~~

- `Sphinx-based documentation is reinitialized`__ in the monorepo. Previous
  iteration based on a central :command:`git` repository and :command:`git`
  submodules is deemed unsuitable, however current project documentation
  published on ReadTheDocs is kept in place, waiting before role documentation
  is fully migrated.

.. __: https://github.com/debops/debops/tree/89dd6fe1a3

- `New Travis CI test suite is introduced`__ that focuses on syntax, testing
  Python scripts, YAML documents, project documentation and :command:`git`
  repository integrity. DebOps roles are not tested directly on Travis anymore.

.. __: https://github.com/debops/debops/tree/6a4da14c60

- `Support for Docker containers is introduced`__ in the monorepo, along with
  an `official 'debops/debops' Docker image`__ which is automatically rebuilt
  and published on any changes in the repository.

.. __: https://github.com/debops/debops/tree/18830a614e
.. __: https://hub.docker.com/r/debops/debops/

December 2017
~~~~~~~~~~~~~

- `New test suite based on GitLab CI is introduced`__ which allows testing of
  the DebOps roles using Vagrant, LXC and KVM/libvirt stack.

.. __: https://github.com/debops/debops/tree/a879a82d5a


2018
----

January 2018
~~~~~~~~~~~~

- `DebOps role documentation is moved to the 'docs/' directory`__ and the
  project documentation published on ReadTheDocs is switched to the DebOps
  monorepo version.

.. __: https://github.com/debops/debops/tree/07dccc3213

May 2018
~~~~~~~~

- End of Debian Wheezy `LTS support`__.

.. __: https://wiki.debian.org/LTS


2019
----

May 2019
~~~~~~~~

- `First DebOps stable release - v1.0.0`__.

.. __: https://lists.debops.org/pipermail/debops-users/2019-May/000196.html

July 2019
~~~~~~~~~

- `Debian 10.0 (buster)`__ becomes a Debian Stable release.

.. __: https://www.debian.org/releases/buster/

2020
----

April 2020
~~~~~~~~~~

- End of Debian Jessie `LTS support`__.

.. __: https://wiki.debian.org/LTS
