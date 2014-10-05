|DebOps| smstools
#################

.. |DebOps| image:: http://debops.org/images/debops-small.png
   :target: http://debops.org

|Travis CI| |test-suite| |Ansible Galaxy|

.. |Travis CI| image:: http://img.shields.io/travis/debops/ansible-smstools.svg?style=flat
   :target: http://travis-ci.org/debops/ansible-smstools

.. |test-suite| image:: http://img.shields.io/badge/test--suite-ansible--smstools-blue.svg?style=flat
   :target: https://github.com/debops/test-suite/tree/master/ansible-smstools/

.. |Ansible Galaxy| image:: http://img.shields.io/badge/galaxy-debops.smstools-660198.svg?style=flat
   :target: https://galaxy.ansible.com/list#/roles/1601



This is an Ansible role which configures `smstools`_ package and sets up
a TCP -> SMS and mail -> SMS gateway. This role has been tested on Debian
and should work on Debian-based systems.

Several other roles from `DebOps`_ project are used to configure various
parts of the SMS gateway (``debops.postfix`` role is used to create mail ->
SMS gateway, ``debops.etc_services``, ``debops.ferm`` and
``debops.tcpwrappers`` are used to configure TCP service which can be used
by other hosts to send SMS messages over the network).

.. _smstools: http://smstools3.kekekasvi.com/
.. _DebOps: http://debops.org/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

::

    ansible-galaxy install debops.smstools

Are you using this as a standalone role without DebOps?
=======================================================

You may need to include missing roles from the `DebOps common playbook`_
into your playbook.

`Try DebOps now`_ for a complete solution to run your Debian-based infrastructure.

.. _DebOps common playbook: https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml
.. _Try DebOps now: https://github.com/debops/debops/


Role dependencies
~~~~~~~~~~~~~~~~~

- ``debops.ferm``- ``debops.etc_services``- ``debops.postfix``- ``debops.tcpwrappers``- ``debops.rsyslog``

Role variables
~~~~~~~~~~~~~~

List of default variables available in the inventory:

::

    ---
    
    # ---- TCP -> SMS gateway ----
    
    # List of IP addresses or CIDR network ranges which are allowed to access TCP
    # service
    smstools_service_allow: []
    
    
    # ---- mail -> SMS gateway ----
    
    # Settings for subdomains and domains which are used to send messages to SMS
    # gateway
    
    # Subdomain for SMS transport
    smstools_mail_transport_subdomain: 'sms'
    
    # Subdomain for mail aliases which are resolved to mobile numbers
    smstools_mail_alias_subdomain: 'gsm'
    
    # Domains that combine above subdomains with main host domain
    smstools_mail_transport_domain: '{{ smstools_mail_transport_subdomain }}.{{ ansible_domain }}'
    smstools_mail_alias_domain: '{{ smstools_mail_transport_subdomain }}.{{ ansible_domain }}'
    
    # List of default mail senders that are allowed to send mail messages to mobile
    # recipients
    # Options:
    #    - name: 'mail@example.com'            # required
    #      state: 'permit/deny'                # optional
    smstools_default_senders:
      - name: 'root@{{ ansible_domain }}'
      - name: '{{ ansible_ssh_user }}@{{ ansible_domain }}'
    
    # Additional list of mail senders
    smstools_senders: []
    
    # Hash table which specifies mail alias to mobile number mapping. Aliases will
    # be generated in a domain specified with smstools_mail_alias_* variables
    smstools_mail_recipients: {}
      #'recipient1': [ '+00123123123' ]
      #'recipient2': [ '+00123123123', '+00321321321' ]
    
    # Hash table which specifies aliases for groups of recipients from
    # smstools_mail_recipients table. Aliases will be created in a domain specified
    # with smstools_mail_alias_* variables
    smstools_mail_aliases: {}
      #'alias': [ 'recipient1', 'recipient2' ]
    
    # List of regexps which will be used to find and remove strings in SMS messages
    # before they are sent
    smstools_mail_msgdel_list: []
      #- 'linux'
      #- '^Ansible'
    
    # Log sent SMS messages for accounting purposes, use monthly log rotation, logs
    # should be kept for 2 years
    smstools_sms_log: '/var/log/sms.log'
    smstools_sms_log_rotation: 'monthly'
    smstools_sms_log_rotation_interval: '{{ (12 * 2) }}'
    
    
    # ---- SMS gateway testing ----
    
    # List of mobile numbers to send a test message to on host reboot
    # Example: [ '+00123123123' ]
    smstools_test_recipients: []
    
    # Test message to send on host reboot
    smstools_test_message: 'This is a test of the SMS gateway on {{ ansible_fqdn }} sent at $(date)'
    
    
    # ---- smstools options ----
    
    # Time between queue checks, in seconds
    smstools_sleep: 1
    
    # Generate modem stats once a day
    smstools_stats_interval: '{{ (60 * 60 * 24)|round|int }}'
    
    # Hash with options configured in /etc/smsd.conf
    smstools_global_options:
      delaytime: '{{ smstools_sleep }}'
      delaytime_mainprocess: '{{ smstools_sleep }}'
      receive_before_send: no
      autosplit: 3
      loglevel: 5
    
    # List of modems known to smsd, by default it's configured to use one modem on
    # serial interface
    smstools_devices:
      - name: 'GSM1'
        device: '/dev/ttyS0'
        options:
          baudrate: 115200
          incoming: yes


Detailed usage guide
~~~~~~~~~~~~~~~~~~~~

Sending a text message from command line
========================================

You can send SMS messages from the host connected to the GSM modem, by running
command:

::

    sudo -u smsd sendsms +00123123123 "Text message"

Your user needs to be in ``sms`` system group or needs to be able to run
``/usr/local/bin/sendsms`` script (for example have admin access).

Sending a text message using TCP service
========================================

SMS messages can be sent remotely using TCP service (by default configured on
port ``9898``). Access to the service is protected using tcpwrappers (via
``xinetd`` service) and iptables firewall.

To send a text message using TCP service, connect to port ``9898`` (by default)
and send string similar to (notice lack of quotation marks):

::

    TEXT +00123123123 Text message

TCP service should respond with text ending with ``250 SMS accepted`` (if
formatting was correct), or ``500 Command not recognized`` (if formatting
was incorrect).

Example telnet session which sends SMS message from a localhost:

::

    $ telnet localhost sms
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    TEXT +00123123123 Text message
    --
    Text: Text message
    To: +00123123123
    250 SMS accepted
    Connection closed by foreign host.

Sending a text message over mail
================================

``debops.smstools`` role configures two subdomains in local Postfix instance:

  - ``sms.`` subdomain is responsible for mail to SMS transport, Postfix takes
    mail messages sent to that subdomain and passes them to ``sms`` service
    (configured in ``/etc/postfix/master.cf`` which is a script that parses the
    mail message and sends body of that message to specified recipient using
    ``sendsms`` script;

  - ``gsm.`` subdomain is used for aliases which correspond to addresses in the
    ``sms.`` subdomain or groups of aliases in the same subdomain;

To send a SMS message via mail, send a mail to an address
``<+00123123123@sms>`` (on localhost) or ``<+00123123123@sms.example.com>``
(from elsewhere). You can also create mail aliases using
``debops.smstools`` role variables or your configured alias table in format
``<name@gsm>`` (from localhost) or ``<name@gsm.example.com>`` (from
elsewhere) which should correspond to mail addresses outlined previously.
Subject of the mail message will be ignored, and body of the message will
be sent using SMS gateway.

Warning, this role can generate mail backscatter!
=================================================

At the moment, SMTP server is configured by ``debops.smstools`` role to accept mail
messages to subdomains specified above and relay them to ``sms`` transport which
checks if a sender of mail message can send SMS messages through mail. If it
can't, SMTP server receives a reject message and generates a bounce message to
an original sender of the mail, which can be forged, generating `mail backscatter`_.

Because of that risk, at the moment mail -> SMS gateway should be configured on
a separate host behind a trusted mail relay to avoid receiving messages from
unknown mail senders, and should only process mail messages from hosts included
in ``mynetworks`` Postfix configuration variable.

To fix backscatter issue, ``debops.smstools`` role needs to have an
`external Postfix access policy service`_ which will be used by Postfix to
check if a specific mail sender can send SMS messages using the gateway.
Steps to determine that:

- check recipient domain of a mail message,
  * if recipient domain is one of the supported subdomains (``sms.`` or ``gsm.``),
    check mail address or domain of the sender against list of allowed
    senders,
    - if mail sender can send SMS messages, return ``PERMIT`` (or ``DUNNO`` if
      other checks should be performed),
    - if mail sender is not found, return ``REJECT``,
  * otherwise (mail recipient not in a supported domain), return ``DUNNO`` to
    allow other checks to perform.

Policy service check should be included in ``smtpd_recipient_restrictions`` list
to be able to check both recipient and sender addresses.

.. _mail backscatter: https://en.wikipedia.org/wiki/Backscatter_\(email\)
.. _external Postfix access policy service: http://www.postfix.org/SMTPD_POLICY_README.html

Known bugs
==========

- ``sendsms`` script supports sending SMS messages in UTF-8, but ``sms-service``
  and ``sms-transport`` scripts do not, SMS messages are truncated at first
  UTF-8 character.


Authors and license
~~~~~~~~~~~~~~~~~~~

``smstools`` role was written by:

- Maciej Delmanowski | `e-mail <mailto:drybjed@gmail.com>`_ | `Twitter <https://twitter.com/drybjed>`_ | `GitHub <https://github.com/drybjed>`_

License: `GPLv3 <https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29>`_

****

This role is part of the `DebOps`_ project. README generated by `ansigenome`_.

.. _DebOps: http://debops.org/
.. _Ansigenome: https://github.com/nickjj/ansigenome/
