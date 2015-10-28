Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

This role installs ``ansible`` APT package for Ansible support. However, the
package from official distribution repositories might be outdated or even not
exist at all. Because of that, if you need to, you can disable ``ansible``
package installation using separate lit variable.

An alternative is to build stable Ansible ``.deb`` package on a spare build
host and provide it using local APT repository. That way, role will
automatically install the correct Ansible version and will be ready to go.

Another alternative is to disable APT Ansible package and enable installation
from PyPI alongside ``debops`` package. However, APT method is preferred, since
it automatically installs all required APT packages.

``debops.debops`` role will install the DebOps playbooks and roles from GitHub
in the background, using either ``batch`` command from the ``at`` package, or
if the former is not available, ``async`` Ansible task. Keep in mind that
downloading all of the repositories might take a while and the code won't be
available for some time after initial Ansible playbook run.

Example inventory
-----------------

To install DebOps on a remote host, you need to add it to
``[debops_recursively]`` Ansible host group::

    [debops_recursively]
    hostname

Example playbook
----------------

Here's an example playbook that installs DebOps support on a host::

    ---
    - name: Install DebOps recursively
      hosts: 'debops_recursively'
      become: True

      roles:

        - role: debops.debops
          tags: [ 'role::debops' ]

