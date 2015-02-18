postfix_dependent_mastercf
~~~~~~~~~~~~~~~~~~~~~~~~~~

This list can be used to configure services in Postfix master.cf using
Postfix dependency variables. Configured services will be saved in Ansible
facts and updated when necessary.

Parameters
''''''''''

Optional parameters from master.cf:
- ``private``
- ``unpriv``
- ``chroot``
- ``wakeup``
- ``maxproc``

You can also specify ``capability`` or ``no_capability`` to define when
a particular service should be configured


Examples
''''''''

Minimal service using ``pipe`` command::

    postfix_dependent_mastercf:
      - service: 'mydaemon'
        type: 'unix'
        command: 'pipe'
        options: |
          flagsd=FR user=mydaemon:mydaemon
          argv=/usr/local/bin/mydaemon.sh ${nexthop} ${user}

