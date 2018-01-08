Troubleshooting
===============

In case of any errors during backup, ``debops.rsnapshot`` role collects output
of all scripts and sends it if anything shows up to ``<backup>`` e-mail
account. With default :ref:`debops.postfix` configuration, this account is aliased
to ``root`` account, so all e-mails should be forwarded to the system
administrator.

Logs for each server configuration are stored in :file:`/var/log/rsnapshot/`
directory, and are automatically rotated.

Fixing issues with SSH host fingerprints
----------------------------------------

When hosts are reinstalled, SSH host fingerprints might be changed in which
case `:program:`rsnapshot` will send e-mails to system administrator. To fix these
errors, you can use a special set of a variable and tag::

    debops --tags role::rsnapshot:sshkeys --extra-vars='rsnapshot_reset_sshkeys=True'

This command will remove all known SSH host fingerprints from
:file:`/root/.ssh/known_hosts` on the backup clients and rescan the hosts, as well
as reinstall the `:program:`rsnapshot` SSH keys on backup servers if necessary.

``rsnapshot_reset_sshkeys`` variable, if ``True``, will always remove SSH host
fingerprints, therefore it shouldn't be used in the Ansible inventory to avoid
idempotency issues.

