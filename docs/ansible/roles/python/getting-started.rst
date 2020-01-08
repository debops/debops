Getting started
===============

.. contents::
   :local:


Support for multiple Python versions
------------------------------------

The role allows management of multiple Python versions at the same time. The
available Python version is dependent on the OS release used on a given host.

Separate default variables can be used to specify APT packages to install for
Python 2.x and Python 3.x series. The different Python versions can then be
enabled or disabled independently - role automatically disables Python
3 support on older OS releases without adequate versions available, and
disables Python 2 support if Ansible is configured to use Python 3 interpreter
on a given host, or Python 3.x is autodetected as the Python interpreter on
Ansible Controller.


Python environment bootstrapping
--------------------------------

The special "raw" mode of operation with a custom Ansible playbook that doesn't
gather Ansible facts automatically can be used to "bootstrap" Python support on
a host. Role will automatically purge an existing Python 2.x packages if Python
2.x operation is disabled; this can be leveraged to maintain Python 3.x-only
setup, depending on the OS release used on the host.


Example inventory
-----------------

The ``debops.python`` role is included by default in the ``common.yml`` DebOps
playbook; you don't need to add hosts to any Ansible groups to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.python`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/python.yml
   :language: yaml

There's a separate Ansible playbook that allows usage of the ``debops.python``
role in a "raw" mode, without fact gathering. This can be used to bootstrap
Python support on a host, so that normal Ansible modules can be used
afterwards:

.. literalinclude:: ../../../../ansible/playbooks/service/python_raw.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::python``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.python`` Ansible role:

- Manual pages: :man:`python(1)`, :man:`pip(1)`, :man:`virtualenv(1)`
- `Debian Python Policy`__
- `Python page`__ in Debian Wiki
- `Status of Python 3 packages in Debian`__
- `Debian plans for Python 3`__ article in Linux Weekly News
- `Python page`__ in Ubuntu Wiki
- `Python (programming language)`__ in Wikipedia
- `import antigravity`__

.. __: https://www.debian.org/doc/packaging-manuals/python-policy/
.. __: https://wiki.debian.org/Python
.. __: https://wiki.debian.org/Python/Python3Packages
.. __: https://lwn.net/Articles/642334/
.. __: https://wiki.ubuntu.com/Python
.. __: https://en.wikipedia.org/wiki/Python_(programming_language)
.. __: https://xkcd.com/353/
