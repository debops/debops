|DebOps| postfix
################

.. |DebOps| image:: http://debops.org/images/debops-small.png
   :target: http://debops.org

|Travis CI| |test-suite| |Ansible Galaxy|

.. |Travis CI| image:: http://img.shields.io/travis/debops/ansible-postfix.svg?style=flat
   :target: http://travis-ci.org/debops/ansible-postfix

.. |test-suite| image:: http://img.shields.io/badge/test--suite-ansible--postfix-blue.svg?style=flat
   :target: https://github.com/debops/test-suite/tree/master/ansible-postfix/

.. |Ansible Galaxy| image:: http://img.shields.io/badge/galaxy-debops.postfix-660198.svg?style=flat
   :target: https://galaxy.ansible.com/list#/roles/1589



This role installs and manages `Postfix`_, an SMTP server.

``debops.postfix`` role is designed to manage Postfix on different hosts in
a cluster, with different "capabilities". At the moment role can configure
Postfix to act as:

* a null client: Postfix sends all mail to another system specified
  either via DNS MX records or an Ansible variable, no local mail is enabled
  (this is the default configuration);
* a local SMTP server: local mail is delivered to local user accounts;
* a network SMTP server: network access is enabled separately from other
  capabilities, to avoid exposing misconfigured SMTP server by mistake and
  becoming an open relay;
* an incoming MX gateway: Postfix will listen on the port 25 (default SMTP
  port) and process connections using ``postscreen`` daemon with automatic
  greylisting and optional RBL checking;
* an outgoing SMTP client: Postfix will relay outgoing mail messages to
  specified remote MX hosts, you can optionally enable SMTP client
  authentication, passwords will be stored separate from the inventory in
  ``secret/`` directory (see ``debops.secret`` role). Sender dependent
  authentication is also available.

More "capabilities" like user authentication, support for virtual mail,
spam/virus filtering and others will be implemented in the future.

This role can also be used as a dependency of other roles which then can
enable more features of the Postfix SMTP server for their own use. For
example, ``debops.mailman`` role enables mail forwarding to the configured
mailing lists, and ``debops.smstools`` role uses Postfix as mail-SMS gateway.

.. _Postfix: http://postfix.org/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

::

    ansible-galaxy install debops.postfix

Are you using this as a standalone role without DebOps?
=======================================================

You may need to include missing roles from the `DebOps common playbook`_
into your playbook.

`Try DebOps now`_ for a complete solution to run your Debian-based infrastructure.

.. _DebOps common playbook: https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml
.. _Try DebOps now: https://github.com/debops/debops/


Role dependencies
~~~~~~~~~~~~~~~~~

- ``debops.ferm``- ``debops.secret``- ``debops.pki``

Role variables
~~~~~~~~~~~~~~

List of default variables available in the inventory:

::

    ---
    
    # Active Postfix capabilities (see README.md). By default Postfix is configured
    # with local mail disabled, all mail is sent to local domain MX server
    postfix: [ 'null' ]
    
    
    # Configuration options for Postfix. Many options are configured automatically
    # using templates, here you can (mostly) add your own entries to Postfix lists
    # (look in Postfix manual for details), they will by added or replaced in
    # templates.
    
    # Mail host name configured in /etc/mailname
    postfix_mailname: '{{ ansible_fqdn }}'
    
    # How long to wait before notifying users about delivery problems
    postfix_delay_warning_time: '4h'
    
    # Address of mail host this host should relay all mail to instead of delivering
    # it directly. (Automatic configuration)
    postfix_relayhost: False
    
    # List of relay domains this host accepts
    postfix_relay_domains: []
    
    # On what interfaces postfix should listen to by default (not a list). (Automatic configuration)
    postfix_inet_interfaces: False
    
    # List of local domains accepted by postfix. (Automatic configuration)
    postfix_mydestination: []
    
    # List of networks postfix accepts by default. (localhost is always enabled)
    postfix_mynetworks: []
    
    # List of postfix transport maps. (Automatic configuration)
    postfix_transport_maps: []
    
    # List of postfix virtual alias maps. (Automatic configuration)
    postfix_virtual_alias_maps: []
    
    # Message size limit in megabytes
    postfix_message_size_limit: 50
    
    
    # TLS certificate configuration (see 'pki' role). By default postfix relies on
    # self-signed certificates, but signed or wildcard certificates can also be
    # enabled.
    postfix_pki: '/srv/pki'
    postfix_pki_type: 'selfsigned'
    postfix_pki_wildcard: '{{ ansible_domain }}'
    postfix_pki_name: '{{ ansible_fqdn }}'
    postfix_pki_cert: False
    postfix_pki_key: False
    
    
    # Firewall configuration. Set these variables to True to enable access for all
    # Internet hosts, or provide lists of allowed IP addresses or address ranges
    # for ports smtp (25), submission (587) or smtps (465). Set to False to
    # deny access from remote hosts.
    postfix_allow_smtp: True
    postfix_allow_submission: True
    postfix_allow_smtps: True
    
    
    # A map of SMTP SASL passwords used in SMTP client authentication by Postfix.
    # You need to add 'client' in postfix capabilities to enable this feature.
    # Format of the entries:
    #   'smtp.example.org': 'username'
    #   'user@example.org': 'username'
    # Passwords are stored in a secret directory, in path:
    # 'secret/credentials/{{ ansible_fqdn }}/postfix/smtp_sasl_password_map/{{ key }}/{{ value }}'
    # - key   = hostname or email address of the sender
    # - value = username on the remote host
    # Postfix role will generate random passwords by default. To change them to
    # your actual passwords, open the files with passwords in the secret directory
    # and replace them, then re-run the playbook with the role.
    postfix_smtp_sasl_password_map: {}
    
    # A map of sender dependent relayhosts used in SMTP client mail relay by Postfix.
    # You need to add 'client' and 'sender_dependent' in postfix capabilities to
    # enable this feature.
    # Format of the entries:
    #   'sender-address': 'relay-host'
    #   'user@example.org': '[smtp.example.org]:submission'
    postfix_sender_dependent_relayhost_map: {}
    
    
    # Mail archive configuration
    # Archiving is enabled by 'archive' option in Postfix capabilities.
    # Remember that an archive account on the receiving server needs to exist.
    
    # Method of archiving:
    #   - 'all':            send all mail without sorting
    #   - 'domain':         send mail sorted by domain
    #   - 'domain-account': send mail sorted by domain and account, divided by separator
    postfix_archive_method: 'all'
    
    # Optional address of a mail account to send the archived mails to. If not
    # specified, Ansible will generate an address by itself in format:
    #   - postfix_archive_account @ ansible_fqdn (if local mail is enabled)
    #   - postfix_archive_account @ postfix_archive_subdomain.ansible_domain
    #     (if local mail is disabled).
    postfix_archive_to: ''
    
    # Mail account to send archived mail to (used by Ansible to generate archive address).
    postfix_archive_account: 'mail-archive'
    
    # Subdomain part of a domain used to generate archive address, if 'local' mail
    # is not enabled in Postfix capabilities (dot at the end is required).
    postfix_archive_subdomain: 'archive.'
    
    # Separator used to separate domain and account part in sorted archive mails.
    # If you use virtual mail delivery, you can sort mail into subdirectories by
    # setting separator as '/' (does not work on local mail delivery).
    postfix_archive_separator: '='
    
    # List of domains to archive, if it's empty, everything is archived.
    postfix_archive_domains: []
    
    
    # Postscreen blacklists
    postfix_postscreen_dnsbl_sites:
    
      # Spamhaus ZEN: http://www.spamhaus.org/zen/
      # Might require registration
      - 'zen.spamhaus.org*3'
    
      # Barracuda Reputation Block List: http://barracudacentral.org/rbl
      # Requires registration
      #- 'b.barracudacentral.org*2'
    
      # Spam Eating Monkey: http://spameatingmonkey.com/lists.html
      # Might require registration
      - 'bl.spameatingmonkey.net*2'
      - 'backscatter.spameatingmonkey.net*2'
    
      # SpamCop Blocking List: http://www.spamcop.net/bl.shtml
      - 'bl.spamcop.net'
    
      # Passive Spam Block List: http://psbl.org/
      - 'psbl.surriel.com'
    
      # mailspike: http://mailspike.net/usage.html
      # Might require contact
      - 'bl.mailspike.net'
    
    
    # Postscreen whitelists
    postfix_postscreen_dnswl_sites:
    
      # SpamHaus Whitelist: http://www.spamhauswhitelist.com/en/usage.html
      # Might require registration
      - 'swl.spamhaus.org*-4'
    
      # DNS Whitelist: http://dnswl.org/tech
      # Might require registration
      - 'list.dnswl.org=127.[0..255].[0..255].0*-2'
      - 'list.dnswl.org=127.[0..255].[0..255].1*-3'
      - 'list.dnswl.org=127.[0..255].[0..255].[2..255]*-4'
    
    
    # List of user-supplied smtpd restrictions, they will replace restrictions
    # automatically created by templates.
    postfix_smtpd_client_restrictions: []
    postfix_smtpd_helo_restrictions: []
    postfix_smtpd_sender_restrictions: []
    postfix_smtpd_relay_restrictions: []
    postfix_smtpd_recipient_restrictions: []
    postfix_smtpd_data_restrictions: []
    
    
    # List of default recipients for local aliases which have no recipients
    # specified, by default current $USER managing Ansible
    postfix_default_local_alias_recipients: ['{{ lookup("env","USER") }}']
    
    # Hash of local aliases which will be merged with default aliases in
    # vars/main.yml. Commented out example below.
    postfix_local_aliases:
      #'alias': [ 'account1', 'account2' ]
      #'other': [ 'user@email', '"|/dir/command"' ]
      #'blackhole': [ '/dev/null' ]
      #'default_recipients':
    
    
    # Custom configuration added at the end of /etc/postfix/main.cf (use text block)
    postfix_local_maincf: False
    
    # Custom configuration added at the end of /etc/postfix/master.cf (use text block)
    postfix_local_mastercf: False
    
    
    # This variable can be used in postfix dependency role definition to configure
    # additional lists used in Postfix main.cf configuration file. This variable
    # will be saved in Ansible facts and updated when necessary
    postfix_dependent_lists: {}
      # Examples:
    
      # Include these lists in transport_maps option
      #transport_maps: ['hash:/etc/postfix/transport']
    
      # Include this alias map if Postfix has 'local' capability
      #alias_maps:
      #  - capability: 'local'
      #    list: [ 'hash:/etc/aliases' ]
    
      # Include this virtual alias map if Postfix does not have 'local' capability
      #virtual_alias_maps:
      #  - no_capability: 'local'
      #    list: [ 'hash:/etc/postfix/virtual_alias_maps' ]
    
    # Here you can specify Postfix configuration options which should be enabled in
    # main.cf using postfix dependency role definition. Configuration will be saved
    # in Ansible facts and updated when necessary
    postfix_dependent_maincf: []
      # Examples:
    
      # Set this option in main.cf
      #- param: 'local_destination_recipient_limit'
      #  value: '1'
    
      # Enable this option only if 'mx' is in Postfix capabilities
      #- param: 'defer_transports'
      #  value: 'smtp'
      #  capability: 'mx'
    
      # Enable this option only if 'local' is not in Postfix capabilities
      #- param: 'relayhost'
      #  value: 'mx.example.org'
      #  no_capability: 'local'
    
      # If no value is specified, check if a list of the same name as param exists
      # in postfix_dependent_lists and enable it
      #- param: 'virtual_alias_maps'
    
    # This list can be used to configure services in Postfix master.cf using
    # postfix dependency variables. Configured services will be saved in Ansible
    # facts and updated when necessary
    postfix_dependent_mastercf: []
      # Examples:
    
      # Minimal service using 'pipe' command
      #- service: 'mydaemon'
      #  type: 'unix'
      #  command: 'pipe'
      #  options: |
      #    flagsd=FR user=mydaemon:mydaemon
      #    argv=/usr/local/bin/mydaemon.sh ${nexthop} ${user}
    
      # Optional parameters from master.cf:
      # private, unpriv, chroot, wakeup, maxproc
    
      # You can also specify 'capability' or 'no_capability' to define when
      # a particular service should be configured
    
    
    # At what hour DH parameters will be regenerated by a script run by cron
    postfix_cron_dhparams_hour: '3'
    
    # List of clients and networks which will have access to XCLIENT protocol
    # extension when 'test' postfix capability is enabled.
    postfix_smtpd_authorized_xclient_hosts: ['127.0.0.1/32']


Detailed usage guide
~~~~~~~~~~~~~~~~~~~~

List of Postfix capabilities in ``postfix`` variable - what Postfix can and
should do on a host. Set this to ``False`` and disable Postfix support, set it
to ``[]`` and have Ansible not do anything with Postfix (unsupported). Not all
combinations of these capabilities will work correctly (role is still in
beta stage).

- ``null``: Postfix has no local delivery, all mail is sent to a MX for current
  domain. Configuration similar to that presented here:
  http://www.postfix.org/STANDARD_CONFIGURATION_README.html#null_client
  Default. You should remove this capability and replace it with others
  presented below.

- ``local``: local delivery is enabled on current host.

- ``network``: enables access to Postfix-related ports (``25``, ``587``,
  ``465``) in firewall, required for incoming mail to be acceped by
  Postfix.

- ``mx``: enables support for incoming mail on port ``25``, designed for hosts set up
  as MX. Automatically enables ``postscreen`` (without ``dnsbl``/``dnswl`` support),
  anti-spam restrictions.

- ``submission``: enables authorized mail submission on ports ``25`` and
  ``587`` (user authentication is currently not supported and needs to be
  configured separately).

- ``deprecated``: designed to enable obsolete functions of mail system,
  currently enables authorized mail submission on port ``465`` (when
  ``submission`` is also present in the list of capabilities).

- ``client``: enable SASL authentication for SMTP client (for outgoing mail
  messages sent via relayhosts that require user authentication).

- ``sender_dependent``: enable sender dependent SMTP client authentication
  (``client`` capability required)

- ``archive``: BCC all mail (or mail from/to specified domains) passing
  through the SMTP server to an e-mail account on local or remote server.

- ``postscreen``: allows to enable postscreen support on port ``25``
  independently of ``mx`` capability.

- ``dnsbl``: enables support for DNS blacklists in postscreen, automatically
  enables whitelists.

- ``dnswl``: enables support for DNS whitelists in postscreen, without blacklists.

- ``test``: enables "soft_bounce" option and XCLIENT protocol extension for
  localhost (useful in mail system testing).

- ``defer``: planned feature to defer mail delivery.

- ``auth``: planned feature to enable user authentication.


Authors and license
~~~~~~~~~~~~~~~~~~~

``postfix`` role was written by:

- Maciej Delmanowski | `e-mail <mailto:drybjed@gmail.com>`_ | `Twitter <https://twitter.com/drybjed>`_ | `GitHub <https://github.com/drybjed>`_

License: `GPLv3 <https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29>`_

****

This role is part of the `DebOps`_ project. README generated by `ansigenome`_.

.. _DebOps: http://debops.org/
.. _Ansigenome: https://github.com/nickjj/ansigenome/
