.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. include:: ../includes/global.rst

.. _dns_configuration:

DNS Configuration
=================

.. contents::
   :depth: 3


.. _dns_configuration_intro:

Correct DNS configuration is crucial
------------------------------------

Many DebOps roles use the ``ansible_fqdn`` and ``ansible_domain`` variables to
create correct default values. It's recommended that all hosts which are
managed via DebOps have proper DNS entries, which means that they should be
resolvable via DNS by their Fully Qualified Domain Name (hostname + domain
name). The FQDN doesn't have to be accessible from the Internet when the hosts
are on a private network, but it should be possible to resolve the FQDNS
internally. This can be achieved e.g. by selecting a subdomain of your main DNS
domain and configure the DNS servers to advertise the subdomain on your private
subnet(s).


.. _dns_configuration_default_names:

Default DNS Names
-----------------

Some roles use default DNS FQDNs to provide various services (e.g. a web
interface). These default FQDNs are listed below as a help in preparing a DNS
zone for your local setup:

================================= =================================== ==================================================================== ==============================
Role                              Variable                            Default                                                              Example
================================= =================================== ==================================================================== ==============================
:ref:`debops.apt_cacher_ng`       :envvar:`apt_cacher_ng__fqdn`       ``software-cache.`` + ``{{ ansible_domain }}``                       ``software-cache.example.com``
:ref:`debops.bind`                :envvar:`bind__fqdn`                ``dns.`` + :envvar:`bind__domain`                                    ``dns.example.com``
:ref:`debops.docker_registry`     :envvar:`docker_registry__fqdn`     ``registry.`` + :envvar:`docker_registry__domain`                    ``registry.example.com``
:ref:`debops.dokuwiki`            :envvar:`dokuwiki__fqdn`            ``wiki.`` + ``{{ ansible_domain }}``                                 ``wiki.example.com``
:ref:`debops.etesync`             :envvar:`etesync__fqdn`             ``etesync.`` + :envvar:`etesync__domain`                             ``etesync.example.com``
:ref:`debops.gitlab`              :envvar:`gitlab__fqdn`              ``code.`` + :envvar:`gitlab__domain`                                 ``code.example.com``
:ref:`debops.icinga_web`          :envvar:`icinga_web__fqdn`          ``icinga.`` + :envvar:`icinga_web__domain`                           ``icinga.example.com``
:ref:`debops.kibana`              :envvar:`kibana__fqdn`              ``kibana.`` + :envvar:`kibana__domain`                               ``kibana.example.com``
:ref:`debops.librenms`            :envvar:`librenms__fqdn`            ``nms.`` + :envvar:`librenms__domain`                                ``nms.example.com``
:ref:`debops.lxc`                 :envvar:`lxc__net_fqdn`             ``{{ ansible_hostname }}`` + :envvar:`lxc__net_domain`               ``host1.lxc.example.com``
:ref:`debops.lxc`                 :envvar:`lxc__net_domain`           ``lxc.`` + :envvar:`lxc__net_base_domain`                            ``lxc.example.com``
:ref:`debops.mailman`             :envvar:`mailman__fqdn`             ``lists.`` + :envvar:`mailman__domain`                               ``lists.example.com``
:ref:`debops.miniflux`            :envvar:`miniflux__fqdn`            ``miniflux.`` + :envvar:`miniflux__domain`                           ``miniflux.example.com``
:ref:`debops.mosquitto`           :envvar:`mosquitto__fqdn`           ``mqtt.`` + :envvar:`mosquitto__domain`                              ``mqtt.example.com``
:ref:`debops.netbox`              :envvar:`netbox__fqdn`              ``dcim.`` + :envvar:`netbox__domain`                                 ``dcim.example.com``
:ref:`debops.netbox`              :envvar:`netbox__fqdn`              ``ipam.`` + :envvar:`netbox__domain`                                 ``ipam.example.com``
:ref:`debops.owncloud`            :envvar:`owncloud__fqdn`            ``cloud.`` + :envvar:`owncloud__domain`                              ``cloud.example.com``
:ref:`debops.pdns`                :envvar:`pdns__nginx_fqdn`          ``powerdns.`` + ``{{ ansible_domain }}``                             ``powerdns.example.com``
:ref:`debops.phpipam`             :envvar:`phpipam__fqdn`             ``ipam.`` + ``{{ ansible_domain }}``                                 ``ipam.example.com``
:ref:`debops.rabbitmq_management` :envvar:`rabbitmq_management__fqdn` ``rabbitmq.`` + :envvar:`rabbitmq_management__domain`                ``rabbitmq.example.com``
:ref:`debops.roundcube`           :envvar:`roundcube__fqdn`           ``webmail.`` + :envvar:`roundcube__domain`                           ``webmail.example.com``
:ref:`debops.rspamd`              :envvar:`rspamd__nginx_fqdns`       ``rspamd.`` + ``{{ ansible_domain }}``                               ``rspamd.example.com``
:ref:`debops.rspamd`              :envvar:`rspamd__nginx_fqdns`       ``{{ ansible_hostname }}`` + ``-rspamd.`` + ``{{ ansible_domain }}`` ``host1-rspamd.example.com``
:ref:`debops.rstudio_server`      :envvar:`rstudio_server__fqdn`      ``rstudio.`` + :envvar:`rstudio_server__domain`                      ``rstudio.example.com``
:ref:`debops.secret`              :envvar:`secret__ldap_fqdn`         ``ldap.`` + :envvar:`secret__ldap_domain`                            ``ldap.example.com``
``debops.foodsoft``               ``foodsoft__fqdn``                  ``foodsoft.`` + ``foodsoft__domain``                                 ``foodsoft.example.com``
``debops.homeassistant``          ``homeassistant__fqdn``             ``ha.`` + ``homeassistant__domain``                                  ``ha.example.com``
================================= =================================== ==================================================================== ==============================


.. _dns_configuration_srv:

DNS SRV Records
---------------

Several DebOps roles (and other software) use `DNS Service (SRV) records`__ to
locate various services. The ``SRV`` record is defined in :rfc:`2782` and has
the following form:

.. __: https://en.wikipedia.org/wiki/SRV_record

.. code-block:: none

  _service._proto.name. ttl IN SRV priority weight port target.

``_service``
  The symbolic name of the desired service, prefixed with an underscore. A list
  of known service names and port numbers is maintained by the `IANA`__ and
  published as the `Service Name and Transport Protocol Port Number Registry`__.

  .. __: https://www.iana.org/
  .. __: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml

``_proto``
  The protocol to use for the desired service, usually ``tcp`` or ``udp``,
  prefixed with an underscore.

``name``
  The domain name for which the record is valid.

``ttl``
  The DNS time-to-live value.

``IN``
  The DNS record class.

``SRV``
  The DNS record type.

``priority``
  The priority of the record. Clients should attempt to use records with the
  lowest priority first and then use records with higher-valued ``priority``
  as a fallback.

``weight``
  The relative weight for records with the same priority. A higher weight means
  a higher change that the record will be picked. Weights do not have to add up
  to any particular sum.

``port``
  The UDP/TCP port on which the service is provided (see the ``_service`` field
  above).

``target``
  The canonical FQDN of the host providing the service, ending with a dot.


.. _dns_configuration_srv_example1:

Example SRV Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

As an an example, assume that we have a hypothetical service ``foo``, which uses
TCP port 4242. The corresponding DNS records might look something like this
(using the ISC BIND zone file format):

.. code-block:: none

  # name                   ttl   class A   IPv4 address
  foo1.example.com.        86400 IN    A   192.0.2.1
  foo2.example.com.        86400 IN    A   192.0.2.2
  foo3.example.com.        86400 IN    A   192.0.2.3
  foobackup.example.com.   86400 IN    A   192.0.3.1

  # _service._proto.name.  ttl   class SRV priority weight port target.
  _foo._tcp.example.com.   86400 IN    SRV 10       80     4242 foo1.example.com.
  _foo._tcp.example.com.   86400 IN    SRV 10       40     4242 foo2.example.com.
  _foo._tcp.example.com.   86400 IN    SRV 10       40     4242 foo3.example.com.
  _foo._tcp.example.com.   86400 IN    SRV 20       0      4242 foobackup.example.com.

Correctly configured clients would then alternate between using the first three
hosts (which all have priority ``10``). 50% of requests would go to
``foo1`` while 25% of requests would go to ``foo2`` and ``foo3``, respectively.
If all three hosts with priority ``10`` are unavailable, clients would be
expected to connect to ``foobackup``.

.. note:: Many existing clients (including the DebOps roles) will employ a more
          simplistic scheme, e.g. by picking the server with the lowest priority
          and highest weight, or just pick a random server. ``SRV`` records can
          therefore not guarantee proper load balancing.


.. _dns_configuration_srv_example2:

Example SRV Configuration using CNAMEs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Or, if you want to add another layer of indirection by using ``CNAME`` records
to make it easier to swap out servers without having to reconfigure all clients
(in case the ``SRV`` records are used to create the initial configuration, as
is done for several DebOps roles):

.. code-block:: none

  # name                   ttl   class A      IPv4 address
  foo-server1.example.com. 86400 IN    A      192.0.2.1
  foo-server2.example.com. 86400 IN    A      192.0.2.2
  foo-server3.example.com. 86400 IN    A      192.0.2.3
  foo-server4.example.com. 86400 IN    A      192.0.3.1
  foo-server5.example.com. 86400 IN    A      192.0.4.1

  # _service._proto.name.  ttl   class SRV    priority weight port target.
  _foo._tcp.example.com.   86400 IN    SRV    10       80     4242 foo1.example.com.
  _foo._tcp.example.com.   86400 IN    SRV    10       40     4242 foo2.example.com.
  _foo._tcp.example.com.   86400 IN    SRV    10       40     4242 foo3.example.com.
  _foo._tcp.example.com.   86400 IN    SRV    20       0      4242 foobackup.example.com.

  # alias                  ttl   class CNAME  canonical name
  foo1.example.com.        86400 IN    CNAME  foo-server1.example.com.
  foo2.example.com.        86400 IN    CNAME  foo-server2.example.com.
  foo3.example.com.        86400 IN    CNAME  foo-server3.example.com.
  foobackup.example.com.   86400 IN    CNAME  foo-server4.example.com.
  foo.example.com.         86400 IN    CNAME  foo-server1.example.com.
  foo-test.example.com.    86400 IN    CNAME  foo-server5.example.com.

In the above example, any clients that are used for testing and development
should be configured to connect directly to the ``foo-test.example.com``
server and not use the ``SRV`` records.

.. warning:: The DNS ``SRV`` specification requires the hostnames used as
             targets in ``SRV`` records to be canonical names, and not aliases
             (i.e. the target must point to a hostname with an ``A`` or ``AAAA``
             record and not to a ``CNAME``). Often it will anyway work to point
             a ``SRV`` record to a ``CNAME``, but strictly speaking, it is not
             RFC compliant (see the "Target" definition on page 3 of
             :rfc:`2782`).


.. _dns_configuration_srv_dnsmasq:

SRV Records using dnsmasq
~~~~~~~~~~~~~~~~~~~~~~~~~
Here's how the :man:`dnsmasq(8)` configuration could look for the
:ref:`first example<dns_configuration_srv_example1>`:

.. code-block:: ini

  host-record = foo1.example.com,192.0.2.1
  host-record = foo2.example.com,192.0.2.2
  host-record = foo3.example.com,192.0.2.3
  host-record = foobackup.example.com,192.0.3.1

  srv-host = _foo._tcp.example.com,foo1.example.com,4242,10,80
  srv-host = _foo._tcp.example.com,foo2.example.com,4242,10,40
  srv-host = _foo._tcp.example.com,foo3.example.com,4242,10,40
  srv-host = _foo._tcp.example.com,foobackup.example.com,4242,20,0

Or, for the :ref:`second example<dns_configuration_srv_example2>`:

.. code-block:: ini

  host-record = foo-server1.example.com,192.0.2.1
  host-record = foo-server2.example.com,192.0.2.2
  host-record = foo-server3.example.com,192.0.2.3
  host-record = foo-server4.example.com,192.0.3.1
  host-record = foo-server5.example.com,192.0.4.1

  cname = foo1.example.com,foo-server1.example.com
  cname = foo2.example.com,foo-server2.example.com
  cname = foo3.example.com,foo-server3.example.com
  cname = foobackup.example.com,foo-server4.example.com
  cname = foo.example.com,foo-server1.example.com
  cname = foo-test.example.com,foo-server5.example.com

  srv-host = _foo._tcp.example.com,foo1.example.com,4242,10,80
  srv-host = _foo._tcp.example.com,foo2.example.com,4242,10,40
  srv-host = _foo._tcp.example.com,foo3.example.com,4242,10,40
  srv-host = _foo._tcp.example.com,foobackup.example.com,4242,20,0


.. _dns_configuration_srv_debops_dnsmasq:

SRV Records using debops.dnsmasq
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using the :ref:`debops.dnsmasq` role, the above configuration can
be set in the Ansible inventory, for the
:ref:`first example<dns_configuration_srv_example1>`:

.. code-block:: yaml

   dnsmasq__dns_records:

     - host: 'foo1.example.com'
       address: '192.0.2.1'

     - host: 'foo2.example.com'
       address: '192.0.2.2'

     - host: 'foo3.example.com'
       address: '192.0.2.3'

     - host: 'foobackup.example.com'
       address: '192.0.3.1'

     - srv: '_foo._tcp.example.com'
       target: 'foo1.example.com'
       port: 4242
       priority: 10
       weight: 80

     - srv: '_foo._tcp.example.com'
       target: 'foo2.example.com'
       port: 4242
       priority: 10
       weight: 40

     - srv: '_foo._tcp.example.com'
       target: 'foo3.example.com'
       port: 4242
       priority: 10
       weight: 40

     - srv: '_foo._tcp.example.com'
       target: 'foobackup.example.com'
       port: 4242
       priority: 20
       weight: 0

Or for the :ref:`second example<dns_configuration_srv_example2>`:

.. code-block:: yaml

   dnsmasq__dns_records:

     - host: 'foo-server1.example.com'
       address: '192.0.2.1'

     - host: 'foo-server2.example.com'
       address: '192.0.2.2'

     - host: 'foo-server3.example.com'
       address: '192.0.2.3'

     - host: 'foo-server4.example.com'
       address: '192.0.3.1'

     - cname: 'foo1.example.com'
       target: 'foo-server1.example.com'

     - cname: 'foo2.example.com'
       target: 'foo-server2.example.com'

     - cname: 'foo3.example.com'
       target: 'foo-server3.example.com'

     - cname: 'foobackup.example.com'
       target: 'foo-server4.example.com'

     - cname: 'foo.example.com'
       target: 'foo-server1.example.com'

     - srv: '_foo._tcp.example.com'
       target: 'foo1.example.com'
       port: 4242
       priority: 10
       weight: 80

     - srv: '_foo._tcp.example.com'
       target: 'foo2.example.com'
       port: 4242
       priority: 10
       weight: 40

     - srv: '_foo._tcp.example.com'
       target: 'foo3.example.com'
       port: 4242
       priority: 10
       weight: 40

     - srv: '_foo._tcp.example.com'
       target: 'foo4.example.com'
       port: 4242
       priority: 20
       weight: 0

   dnsmasq__dhcp_hosts:
     - name: 'foo-server5'
       comment: 'Development foo server'
       domain: 'example.com'
       mac: '00:00:5e:00:53:04'
       ip: '192.0.4.1'
       cname: [ 'foo-test' ]

.. note:: The above example demonstrates how host addresses can be defined
          either as a separate ``host`` record in :envvar:`dnsmasq__dns_records`
          *or* as part of a DHCP record in :envvar:`dnsmasq__dhcp_hosts`.


.. _dns_configuration_srv_usage:

SRV Records used by DebOps roles
--------------------------------

The following table lists the DNS ``SRV`` records used for autoconfiguration by
various DebOps roles:

=========================== ========================= ====================================== ============================================================================
Role                        SRV                       Variable                               Fallback
=========================== ========================= ====================================== ============================================================================
:ref:`debops.gitlab_runner` ``_gitlab._tcp``          :envvar:`gitlab_runner__gitlab_srv_rr` ``code.`` + :envvar:`gitlab_runner__domain` + ``:443``
:ref:`debops.icinga`        ``_icinga-master._tcp``   :envvar:`icinga__master_nodes`         ``icinga-master.`` + :envvar:`icinga__domain` + :envvar:`icinga__api_port`
:ref:`debops.icinga`        ``_icinga-director._tcp`` :envvar:`icinga__director_nodes`       ``icinga-director.`` + :envvar:`icinga__domain` + :envvar:`icinga__api_port`
:ref:`debops.imapproxy`     ``_imap._tcp``            :envvar:`imapproxy__imap_srv_rr`       ``imap.`` + :envvar:`imapproxy__domain` + ``:143``
:ref:`debops.imapproxy`     ``_imaps._tcp``           :envvar:`imapproxy__imaps_srv_rr`      ``imap.`` + :envvar:`imapproxy__domain` + ``:993``
:ref:`debops.ldap`          ``_ldap._tcp``            :envvar:`ldap__servers_srv_rr`         ``ldap.`` + :envvar:`ldap__domain` + ``:389``
:ref:`debops.nullmailer`    ``_smtp._tcp``            :envvar:`nullmailer__smtp_srv_rr`      ``smtp.`` + :envvar:`nullmailer__domain` + ``:25``
:ref:`debops.roundcube`     ``_imaps._tcp``           :envvar:`roundcube__imap_srv_rr`       ``imap.`` + :envvar:`roundcube__domain` + ``:993``
:ref:`debops.roundcube`     ``_submissions._tcp``     :envvar:`roundcube__smtp_srv_rr`       ``smtp.`` + :envvar:`roundcube__domain` + ``:465``
:ref:`debops.roundcube`     ``_sieve._tcp``           :envvar:`roundcube__sieve_srv_rr`      ``sieve.`` + :envvar:`roundcube__domain` + ``:4190``
:ref:`debops.rsyslog`       ``_syslog._tcp``          :envvar:`rsyslog__syslog_srv_rr`       ``syslog.`` + :envvar:`rsyslog__domain` + ``:6514``
=========================== ========================= ====================================== ============================================================================


.. _dns_configuration_plugin:

The DebOps dig_srv plugin
-------------------------

DebOps roles use a slightly modified version of the Ansible `dig lookup`__
plugin to perform DNS ``SRV`` record lookups. The reason that a custom plugin
is used is that the Ansible version does not make it possible to distinguish
between errors which should halt the operation of a play (e.g. if the DNS server
returns ``SERVFAIL``) and errors which should not (e.g. ``NXDOMAIN``).

.. __: https://docs.ansible.com/ansible/latest/collections/community/general/dig_lookup.html

In addition, the ansible plugin does not sort the returned resource records,
meaning that idempotency is not ensured (unless the results are sorted manually)
in case several ``SRV`` records are returned.

The custom ``dig_srv`` plugin generally works in a manner similar to the
Ansible ``dig`` lookup plugin, but removes parameters which are not necessary
for looking up ``SRV`` resource records and also provides a slightly different
return value.

If we assume a role called ``bar``, which wishes to lookup ``SRV`` records for
the service ``foo``, using ``foo.<domain>`` and port ``4242`` as a fallback
(in case no ``SRV`` records are defined), the plugin would be called like this:

.. code-block:: yaml

  bar__domain: '{{ ansible_domain }}'

  bar__foo_srv_rr: '{{ q("debops.debops.dig_srv", "_foo._tcp." + bar__domain,
                         "foo." + bar__domain, 4242) }}'

The return value from the lookup would be a list of YAML dictionaries, where
each dictionary corresponds to one ``SRV`` record. Something like this:

.. code-block:: yaml

  bar__foo_srv_rr:

    - target: 'foo1.example.com'
      class: 'IN'
      owner: '_foo._tcp.example.com'
      port: 4242
      priority: 10
      ttl: 86400
      type: 'SRV'
      weight: 40
      dig_srv_src: 'dns'
      target_port: 'foo1.example.com:4242'

    - target: 'foo2.example.com'
      class: 'IN'
      owner: '_foo._tcp.example.com'
      port: 4242
      priority: 20
      ttl: 86400
      type: 'SRV'
      weight: 40
      dig_srv_src: 'dns'
      target_port: 'foo2.example.com:4242'

The ``dig_srv_src`` field will be either ``dns`` if resource records were
returned by the DNS server and ``fallback`` otherwise. See
:ref:`dns_configuration_srv` for a definition of the other fields.  The
resource records will be sorted on ``priority``, ``weight`` (reverse order,
i.e. higher weight first), ``target`` and ``port``.

In case no ``SRV`` records are available, the lookup will return something like
this:

.. code-block:: yaml

  bar__foo_srv_rr:

    - target: 'foo.example.com'
      class: 'IN'
      owner: '_foo._tcp.example.com'
      port: 4242
      priority: 0
      ttl: 0
      type: 'SRV'
      weight: 0
      dig_srv_src: 'fallback'
      target_port: 'foo.example.com:4242'


.. _dns_configuration_override:

Overriding DNS SRV Queries
--------------------------
The format described in the previous section can also be used to override the
variables used by the various roles to lookup the DNS ``SRV`` records
(generally named ``<role>__*_srv_rr``, see :ref:`dns_configuration_srv_usage`
for a list), for example if you plan to add DNS ``SRV`` records later:

.. code-block:: yaml

   # ansible/inventory/group_vars/all/bar.yml

   bar__foo_srv_rr:
     - target: 'foo.example.org'
       port: '1234'
       priority: '1'

Alternatively, most roles set separate variables on the basis of the results
of the ``SRV`` lookup. In such cases, it might also be more straightforward
to override these "dependent" variables straight away.

For example, the :ref:`debops.nullmailer` role performs the ``SRV`` lookup
using the :envvar:`nullmailer__smtp_srv_rr` variable, which is then used
to create default values for :envvar:`nullmailer__relayhost` and
:envvar:`nullmailer__smtp_port`:

.. code-block:: yaml

  nullmailer__smtp_srv_rr: '{{ q("debops.debops.dig_srv"... }}'

  nullmailer__relayhost: '{{ nullmailer__smtp_srv_rr[0]["target"] }}'

  nullmailer__smtp_port: '{{ nullmailer__smtp_srv_rr[0]["port"] }}'

Which means that the autoconfiguration can also be overridden by setting these
variables directly:

.. code-block:: yaml

  # ansible/inventory/group_vars/all/nullmailer.yml

  nullmailer__relayhost: 'notfoo.example.com'

  nullmailer__smtp_port: 42


.. _dns_configuration_refs:

Further Reading
---------------

- The Wikipedia article on `DNS Service (SRV) records`__

.. __: https://en.wikipedia.org/wiki/SRV_record

- `IANAs`__ list of `service names and port numbers`__

.. __: https://www.iana.org/
.. __: https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml

- :rfc:`2782` - The DNS ``SRV`` specification

- :rfc:`6186` - IMAP / POP / Submission ``SRV`` records

- :rfc:`5804` - ManageSieve ``SRV`` records

- `IETF`__ `draft`__ - Syslog/SNMP ``SRV`` records

.. __: https://ietf.org/
.. __: https://tools.ietf.org/html/draft-schoenw-opsawg-nm-srv-03
