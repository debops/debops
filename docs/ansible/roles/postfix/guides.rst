.. _postfix__ref_guides:

Postfix configuration guides
============================

Here you can find a few guides that can help you configure more advanced
Postfix features. Some of these can and are implemented as separate Ansible
roles, here you can see the configuration specific to ``debops.postfix`` role.


.. _postfix__ref_guides_smtp_auth:

Postfix SMTP client with SASL authentication
--------------------------------------------

This configuration is based on the `SMTP client SASL authentication HOWTO`__.

.. __: http://www.postfix.org/SASL_README.html#client_sasl_enable

We will configure Postfix to act as an SMTP client and send all mail to
a remote relay which requires SMTP authentication. This guide assumes that you
already have an e-mail account set up elsewhere and you know the password.

For SASL authentication to work, Postfix requires ``libsasl2-modules`` package
(there are some custom ones for LDAP, OTP, SQL). You need to tell
``debops.postfix`` role to install one for you, via Ansible inventory:

.. code-block:: yaml

   postfix__packages: [ 'libsasl2-modules' ]

It's best to keep the authentication details out of the Ansible inventory,
therefore you should create a separate text file in the :file:`ansible/secret/`
directory of the project directory (see :ref:`debops.secret` for details).

Create the file :file:`ansible/secret/postfix/smtp-auth.key`. In it, put the
e-mail account username and password in the form:

.. code-block:: none

   username:password

You now need to create a lookup table with the authentication credentials for
Postfix to consume. You can do this using Ansible inventory:

.. code-block:: yaml

   postfix__lookup_tables:

     - name: 'smtp_sasl_password_maps.in'
       mode: '0600'
       options:

         - name: '[smtp.example.org]'
           value: '{{ lookup("file", secret + "/postfix/smtp-auth.key") }}'

The ``.in`` filename suffix tells Postfix to generate a hash table with the
file contents. The files should be secured with the ``0600`` permissions, so
only ``root`` will be able to read it.

The last piece of the puzzle is the Postfix configuration in the
:file:`/etc/postfix/main.cf`. You can set it via Ansible inventory:

.. code-block:: yaml

   postfix__maincf:

     - name: 'smtp_sasl_auth_enable'
       value: True

     - name: 'smtp_tls_security_level'
       value: 'encrypt'

     - name: 'smtp_sasl_tls_security_options'
       value: 'noanonymous'

     - name: 'relayhost'
       value: '[smtp.example.org]'

     - name: 'smtp_sasl_password_maps'
       value: [ 'hash:${config_directory}/smtp_sasl_password_maps' ]

When you run the ``debops.postfix`` role with the above configuration, Postfix
should now send all e-mails to the ``smtp.example.org`` relayhost with SMTP
client authentication. You can send an e-mail and check the logs in
:file:`/var/log/mail.log` to see if they are relayed correctly.
