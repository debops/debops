|DebOps logo| `DebOps <https://debops.org/>`__ documentation
============================================================

*Your Debian-based data center in a box*

A collection of `Ansible <https://ansible.com/>`_ playbooks,
scalable from one container to an entire data center.

.. note::

   The DebOps documentation is currently being reorganized, some of the
   sections might be empty or misleading. Ansible role documentation is
   current for the roles in the `DebOps monorepo`_, the old project
   documentation is available at the end of the ToC.

.. _DebOps monorepo: https://github.com/debops/debops/

.. toctree::
   :caption: Introduction
   :maxdepth: 1

   introduction/quick-start
   introduction/project-goals
   introduction/faq
   introduction/community
   introduction/philosophy
   introduction/timeline

.. toctree::
   :caption: News
   :maxdepth: 1

   news/releases
   news/changelog
   news/upgrades

.. toctree::
   :caption: User Guide
   :maxdepth: 2

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

   developer-guide/development-model
   developer-guide/monorepo-layout
   developer-guide/code-standards
   developer-guide/software-sources
   developer-guide/debops-roadmap

.. toctree::
   :caption: Tester Guide
   :maxdepth: 2

   tester-guide/test-methodology
   tester-guide/travis-ci
   tester-guide/gitlab-ci
   tester-guide/vagrant
   tester-guide/jane
   tester-guide/testinfra

.. toctree::
   :caption: DebOps API
   :maxdepth: 2

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
