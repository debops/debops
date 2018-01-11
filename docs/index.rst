|DebOps logo| `DebOps <https://debops.org/>`__ documentation
============================================================

*Your Debian-based data center in a box*

.. include:: includes/global.rst

This site provides the documentation related to the DebOps project. you can
browse the documentation sections using the sidebar.

.. note::

   The DebOps documentation is currently being reorganized, some of the
   sections might be empty or misleading. Ansible role documentation is
   current for the roles in the `DebOps monorepo`__, the old project
   documentation is available at the end of the ToC.

.. __: https://github.com/debops/debops/

The DebOps project is a set of tools that let users bootstrap and manage
a production environment based on the Debian_ operating system. At the moment
the main tool used for this is Ansible_; DebOps provides
a :ref:`collection of Ansible roles <role_index>`, as well as
a `set of Ansible playbooks`__ that tie them together in a highly integrated environment.

.. __: https://github.com/debops/debops/tree/master/ansible/playbooks

You can use Ansible roles and playbooks provided by DebOps to manage either one
Debian-based host, a set of hosts or an entire data center. The hosts in
question can be physical or virtual machines, or even LXC/Docker containers.

.. toctree::
   :caption: Introduction
   :maxdepth: 1
   :hidden:

   introduction/quick-start
   introduction/project-goals
   introduction/faq
   introduction/community
   introduction/philosophy
   introduction/timeline
   introduction/other-projects
   introduction/references

.. toctree::
   :caption: News
   :maxdepth: 1
   :hidden:

   news/releases
   news/changelog
   news/upgrades

.. toctree::
   :caption: User Guide
   :maxdepth: 2
   :hidden:

   user-guide/install
   user-guide/debops-for-ansible
   user-guide/project-directories
   user-guide/ansible-inventory
   user-guide/site-playbook
   user-guide/debops-cli
   user-guide/debops-config
   user-guide/bugs

.. toctree::
   :caption: Ansible Roles
   :hidden:

   ansible/role-index
   ansible/roles/index

.. toctree::
   :caption: Developer Guide
   :maxdepth: 2
   :hidden:

   developer-guide/development-model
   developer-guide/monorepo-layout
   developer-guide/code-standards
   developer-guide/software-sources
   developer-guide/debops-roadmap

.. toctree::
   :caption: Tester Guide
   :maxdepth: 2
   :hidden:

   tester-guide/test-methodology
   tester-guide/travis-ci
   tester-guide/gitlab-ci
   tester-guide/vagrant
   tester-guide/jane
   tester-guide/testinfra

.. toctree::
   :caption: DebOps API
   :maxdepth: 2
   :hidden:

   debops-api/index

.. toctree::
   :caption: Old documentation
   :maxdepth: 2
   :glob:

   debops-tools/index
   debops-playbooks/index
   debops-policy/index
   philosophy


.. |DebOps logo| image:: _static/images/debops-small.png

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
