.. _postscreen__ref_defaults_detailed:

Default variable details
========================

some of ``debops.postscreen`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _postscreen__ref_access:

postscreen__access
------------------

This is a list of IP addresses or CIDR subnets which can be statically
whitelisted or blacklisted in Postscreen. Entries are processed in order of
appearance. If a list entry is a string, the given entry will be whitelisted.
Otherwise, you can specify an entry as a YAML dictionary with specific keys:

``name``, ``cidr``
  Required. The IP address or CIDR subnet to manage in the access list.

``state``
  Optional. If not specified or ``present``, a given entry will be present in
  the access list. If ``absent``, a given entry will be removed from the access
  list.

``action``, ``value``
  Optional. If ``permit``, a given client will be immediately accepted by
  Postscreen. If ``reject``, a given client will be disconnected by Postscreen.
  if ``dunno``, the accept/reject decision will be left to further checks by
  Postscreen. If action is not specified, by default the entry use the
  ``permit`` action.

``comment``
  Optional. String or YAML text block with a comment about a given entry.

Examples
~~~~~~~~

Allow client connections from private RFC 1918 subnets, except specific
addresses:

.. code-block:: yaml

   postscreen__access:

     - name: '10.0.0.1'
       action: 'dunno'
       comment: 'Local gateway'

     - '10.0.0.0/8'
     - '172.16.0.0/12'
     - '192.168.0.0/16'


.. _postscreen__ref_dnsbl_reply_pcre_map:

postscreen__dnsbl_reply_pcre_map
--------------------------------

This list contains regular expressions that specify the DNS blocklists. When
Postscreen checks the client's IP address against DNS blocklists and a client
is blocked, Postscreen rejects the client's connection with a message. This
list can be used to define what message is sent to the client after it has been
blocked by Postscreen.

You can specify list entries as PCRE regular expressions, in that case they
will use the default response defined in the
:envvar:`postscreen__dnsbl_default_reply`. Alternatively, you can specify
entries as YAML dictionaries with specific parameters:

``name``, ``pcre``
  Required. A regular expression that identifies a DNS Blocklist.

``value``, ``reply``
  Optional. A string that specifies the response sent to the client when its
  connection is blocked by a given DNS Blocklist.

``state``
  Optional. If not specified or ``present``, a given entry will be added in the
  configuration file. If ``absent``, a given entry will be removed from the
  configuration file.

``comment``
  Optional. String or YAML text block with a comment for a given entry.

Examples
~~~~~~~~

Define a custom response for a RBL:

.. code-block:: yaml

   postscreen__dnsbl_reply_pcre_map:

     - pcre: '/^rbl\.example\.org$/'
       reply: 'Blocked by a DNS RBL'
