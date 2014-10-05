|DebOps| monit
##############

.. |DebOps| image:: http://debops.org/images/debops-small.png
   :target: http://debops.org

|Travis CI| |test-suite| |Ansible Galaxy|

.. |Travis CI| image:: http://img.shields.io/travis/debops/ansible-monit.svg?style=flat
   :target: http://travis-ci.org/debops/ansible-monit

.. |test-suite| image:: http://img.shields.io/badge/test--suite-ansible--monit-blue.svg?style=flat
   :target: https://github.com/debops/test-suite/tree/master/ansible-monit/

.. |Ansible Galaxy| image:: http://img.shields.io/badge/galaxy-debops.monit-660198.svg?style=flat
   :target: https://galaxy.ansible.com/list#/roles/1575



``debops.monit`` role allows you to install and configure `Monit`_ service
which can be used to monitor processes, services or even other hosts. You
can also use this role as a dependency of another role and configure
monitoring service for an application this way.

Alerts can be sent to an e-mail address (by default
``monitoring@<your-domain>``, or to a mobile phone or pager using an SMS
gateway (for example one managed by ``debops.smstools`` role).

.. _Monit: http://mmonit.com/monit/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

::

    ansible-galaxy install debops.monit

Are you using this as a standalone role without DebOps?
=======================================================

You may need to include missing roles from the `DebOps common playbook`_
into your playbook.

`Try DebOps now`_ for a complete solution to run your Debian-based infrastructure.

.. _DebOps common playbook: https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml
.. _Try DebOps now: https://github.com/debops/debops/


Role dependencies
~~~~~~~~~~~~~~~~~

- ``debops.etc_services``
- ``debops.apt_preferences``


Role variables
~~~~~~~~~~~~~~

List of default variables available in the inventory:

::

    ---
    
    # ---- Global configuration options ----
    
    # The number of seconds to determine if a process is down or not.
    monit_interval: 60
    
    # The number of seconds before starting to monitor a process which just launched.
    # Set this to 0 to disable it.
    monit_start_delay: 30
    
    # Which facility should monit be syslogged to?
    # An empty string defaults to : 'user'.
    # Another possibility would be: 'facility log_daemon'.
    monit_syslog: ''
    
    
    # ---- E-mail alerts ----
    
    # Where should the alerts get sent to?
    # 'only_on' allows you to optionally send alerts only when certain events occurred:
    # Use a comma separated list to provide more than 1 event.
    # When undefined or blank it will send an alert on all events.
    # https://mmonit.com/monit/documentation/#setting_an_event_filter
    # You can disable alerting completely by providing an empty list.
    monit_mail_alert_to:
      - { email: 'monitoring@{{ ansible_domain }}', only_on: '' }
    
    # Supply a list of mail servers, the first item in the list will be tried first.
    monit_mail_servers:
    
      # Only the host is required.
      - host: 'localhost'
    
        # The port defaults to 25.
        #port: 25
    
        # The username, password and encryption default to undefined.
        #username:
        #password:
    
        # The available encryption types are:
        # SSLAUTO, SSLV2, SSLV3, TLSV1, TLSV11, TLSV12
        #encryption:
    
    # Who sent it and how should the message be formatted?
    monit_mail_from: 'monit@{{ ansible_fqdn }}'
    monit_mail_reply_to: 'monit@{{ ansible_fqdn }}'
    monit_mail_subject: '[Monit] $EVENT $SERVICE'
    monit_mail_message: |
      $EVENT Service $SERVICE
      Date:        $DATE
      Action:      $ACTION
      Host:        $HOST
      Description: $DESCRIPTION
    
      Your faithful employee,
      Monit
    
    # Instead of a big e-mail message you can use a smaller sms-friendly message.
    # Just uncomment it to enable this message styling instead.
    #monit_mail_message_sms: '$ACTION $SERVICE on $HOST: $DESCRIPTION, $DATE'
    
    
    # ---- Process monitoring ----
    
    # Which processes do you want to monitor?
    monit_process_list: []
    
    # The same as process list except scoped to a specific host or group.
    monit_process_group_list: []
    monit_process_host_list: []
    monit_process_dependent_list: []
    
    # Example:
    #monit_process_list:
    
      # The pid path is relative to /var/run, this is required.
      #- pid: ''
    
        # The process is simply the process name, defaults to the pid's basename.
        #process: 'foo'
    
        # Set a timeout, defaults to 60 seconds.
        #timeout: 60
    
        # The sysvinit style to start/stop a process, you can change this per process.
        #start: '/etc/init.d/process start'
        #stop: '/etc/init.d/process stop'
    
        # Append custom script logic, defaults to nothing.
        #script: |
    
        # Stop monitoring the process by deleting the config.
        #delete: False




Authors and license
~~~~~~~~~~~~~~~~~~~

``monit`` role was written by:

- Nick Janetakis | `e-mail <mailto:nick.janetakis@gmail.com>`_ | `Twitter <https://twitter.com/nickjanetakis>`_ | `GitHub <https://github.com/nickjj>`_

License: `GPLv3 <https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29>`_

****

This role is part of the `DebOps`_ project. README generated by `ansigenome`_.

.. _DebOps: http://debops.org/
.. _Ansigenome: https://github.com/nickjj/ansigenome/
