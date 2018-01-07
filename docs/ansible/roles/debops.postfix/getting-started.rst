Getting started
===============

Default configuration
---------------------

The ``debops.postfix`` role configures a basic Postfix SMTP server with
configuration similar to the "Internet Site" configuration enabled by default
by the Debian package. With the default configuration, SMTP service listens for
connections on port ``25`` from all hosts. Mail relay is authorized from
``localhost``, other hosts are deferred. The SMTP server accepts mail addressed
for the host's FQDN, but not it's domain. There's no default relayhost, Postfix
delivers the mail directly to other hosts. Local mail is enabled by default,
support for mail aliases is provided by the ``debops.etc_aliases`` Ansible
role.

Additional configuration is defined in separate variables and can be easily
disabled or modified if necessary. To do that, you can modify the values of the
:envvar:`postfix__combined_maincf` and :envvar:`postfix__combined_mastercf`
variables.

The Postfix service will be configured to use TLS connections and strong
encryption by default. This might interfere with SMTP service operation for
older installations that don't support required features.


Example inventory
-----------------

To install and configure Postfix on a host, it needs to be present in the
``[debops_service_postfix]`` Ansible inventory group:

.. code-block:: none

   [debops_service_postfix]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.postfix`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/postfix.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::postfix``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
