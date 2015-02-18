postfix_smtp_sasl_password_map
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A map of SMTP SASL passwords used in SMTP client authentication by Postfix.
You need to add ``client`` in Postfix capabilities to enable this feature.

Format of the password entries:

- *key*: remote SMTP server hostname or sender e-mail address
- *value*: username on the remote SMTP server

Example entries::

    postfix_smtp_sasl_password_map:
      'smtp.example.org': 'username'
      'user@example.org': 'username'
      'user@example.org': 'username@example.com'

Passwords are stored in a `secret`_ directory, in path::

    secret/credentials/{{ ansible_fqdn }}/postfix/smtp_sasl_password_map/{{ key }}/{{ value }}

If you do not define the passwords there, this role will generate
random passwords by default and store them there. You can use this
to your advantage by running debops once without defining the password
to let debops generate the right location automatically.

Passwords on the remote host are stored in::

    /etc/postfix/private_hash_tables/

To regenerate, change or add new passwords, you need to remove the ``*.lock``
files located in above directory.

.. _secret: https://github.com/debops/ansible-secret/

