Getting started
===============

.. contents::
   :local:

When ``fail2ban`` is installed, an ``ssh`` jail will be configured by default
(by the Debian package, not DebOps).

``debops.fail2ban`` role uses ``iptables`` ``recent`` module instead of adding
the banned hosts to the firewall directly. The ``recent`` rule will be added to
the ``INPUT`` chain at specific location, to work seamlessly with the default
firewall configuration managed by ``debops.ferm`` role. If necessary, you can
specify the location of the rules using custom ``item.position`` parameter.


Example inventory
-----------------

To enable ``fail2ban`` you can add a host or several hosts to
``[debops_fail2ban]`` group::

    [debops_fail2ban]
    hostname

If you have many hosts which you want to protect using ``fail2ban``, you can
instead create a child group and add it to the ``[debops_fail2ban]`` parent
group::

    [debops_fail2ban:children]
    protected_hosts

    [protected_hosts]
    host1
    host2
    host3

To manage jails, you use ``fail2ban_*_jails`` list variables by adding them in
``group_vars/`` or ``host_vars/`` directories. For example, to disable the
``ssh`` jail by default on all hosts, create
``inventory/group_vars/all/fail2ban.yml`` file and add inside::

    ---

    fail2ban_jails:

      - name: 'ssh'
        enabled: 'false'
        comment: 'Disable default ssh jail'


Example playbook
----------------

Here's an example playbook which uses ``debops.fail2ban`` role to install ``fail2ban``::

    ---

    - name: Install fail2ban
      hosts: debops_fail2ban

      roles:
        - role: debops.fail2ban
          tags: fail2ban

