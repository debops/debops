|debops_logo| `DebOps <https://debops.org>`_
============================================

|CII Best Practices|

**Your Debian-based data center in a box**

A collection of `Ansible <https://ansible.com/>`_ playbooks,
scalable from one container to an entire data center.

DebOps is a framework
^^^^^^^^^^^^^^^^^^^^^

- **117+ highly extensible roles** with sane defaults
- **Tuned for production** and works great for development
- **Built for modularity** so extending it is simple
- **Custom scripts** to tie everything together

We believe in the UNIX philosophy; one tool should only do one thing very well.
DebOps has many playbooks and roles but it is just a set of focused tools to
help you run and manage your infrastructure.

In fact all of the DebOps playbooks and roles can be ran with Ansible directly.

Installation
^^^^^^^^^^^^

Dependencies
````````````

DebOps requires a dependency that is not already installed by Ansible.
Install ``netaddr`` however you see fit:

::

   $ pip install netaddr
   $ apt-get install python-netaddr
   $ yum install python-netaddr

DebOps scripts
``````````````

The easiest way to install DebOps is::

   $ sudo pip install https://github.com/debops/debops-tools/archive/master.zip
   $ debops-update

If you want to have more control on the installation process, you can
use::

   $ git clone https://github.com/debops/debops-tools
   $ sudo pip install ./debops-tools
   $ debops-update

Please see the `Installation Guide
<https://docs.debops.org/en/latest/debops/docs/installation.html>`_ for more
details.


Getting started
^^^^^^^^^^^^^^^

Here is a short intro how to use DebOps. Please have a look at the
`Getting Started Guide
<https://docs.debops.org/en/latest/debops-playbooks/docs/guides/getting-started.html>`_ for more
detailed information.

**Make your first project**

::

   $ debops-init ~/myproject

**Add a host to your inventory**

Take a peek at ``~/myproject/ansible/inventory/hosts``.

**Verify it**

::

   $ ssh yourhost
   $ debops-task all -m setup

**Run the DebOps playbooks**

::

   $ debops

What do you want to learn more about?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|Gratipay|_

- `Playbooks and roles <https://github.com/debops/debops-playbooks>`_
- `Custom scripts <https://docs.debops.org/en/latest/debops-playbooks/docs/custom-features.html>`_
- DebOps guides and troubleshooting
    - `Using linux containers <https://docs.debops.org/en/latest/debops-playbooks/docs/guides/linux-containers.html>`_
    - `Creating a local APT server to use backports <https://docs.debops.org/en/latest/debops-playbooks/docs/guides/local-apt-repository.html>`_
    - `Solving common problems <https://github.com/debops/debops-tools/wiki/Solutions-to-problems-you-may-encounter>`_

Do you want to contribute?
^^^^^^^^^^^^^^^^^^^^^^^^^^

Sounds great, check out the `contributing guide <https://docs.debops.org/en/latest/debops/docs/contributing.html>`_
for the details.

Authors
```````

**Maciej Delmanowski**

- Email: drybjed@gmail.com
- Twitter: `@drybjed <https://twitter.com/drybjed>`_
- Github: `drybjed <https://github.com/drybjed>`_

**Nick Janetakis**

- Email: nick.janetakis@gmail.com
- Twitter: `@nickjanetakis <https://twitter.com/nickjanetakis>`_
- Github: `nickjj <https://github.com/nickjj>`_

**Hartmut Goebel**

- Email: h.goebel@crazy-compilers.com
- Website: http://www.crazy-compilers.com

**Robin `ypid` Schneider**

- Email: ypid@riseup.net
- Website: https://me.ypid.de/
- GitHub: `ypid <https://github.com/ypid>`_

.. |Gratipay| image:: https://img.shields.io/gratipay/drybjed.svg?style=flat
.. _Gratipay: https://www.gratipay.com/drybjed/
.. |debops_logo| image:: https://debops.org/images/debops-small.png

.. |CII Best Practices| image:: https://bestpractices.coreinfrastructure.org/projects/237/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/237

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
