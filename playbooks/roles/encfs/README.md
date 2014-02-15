encfs
=====

Ansible role 'encfs' allows you to create and manage directories using [EncFS](https://en.wikipedia.org/wiki/EncFS), FUSE-based encrypted virtual filesystem.

Primary mode of operation is to provide encrypted and secure storage space for passwords and sensitive files on localhost (Ansible Controller) using GPG-encrypted keyfile as password for EncFS. Access to 'root' account (via sudo) is only required during a setup phase to install 'fuse' and 'encfs' packages, and fix `/dev/fuse` access permissions; otherwise role works with a regular user account.

Role supports directories in remote hosts encrypted using a password with optional "passfile" as a transport for passwords in transit.

Requirements
------------

- `sudo` access will be required to install 'fuse' and 'encfs' packages, fix `/dev/fuse` permissions and add current user to 'fuse' group.

- `gpg` will be used to encrypt keyfile for encrypted storage file, either with a passphrase or provided GPG key(s).

Role Variables
--------------

- `encfs`: absolute path to a directory which will be used as the mount point for encrypted filesystem. It will be created if not found. Required.

- `encfs_suffix`: suffix of a secondary directory which holds the actual encrypted filesystem. It will be added to the `encfs` variable. ".encrypted" by default, optional.

- `encfs_gpg`: list of one or more OpenPGP/GnuPG public keys to use for encryption. If this variable is not defined in inventory, GnuPG will ask for a passphrase during storage creation and every time encrypted storage is opened; with OpenPGP/GnuPG keys GnuPG can utilize `gpg-agent` for decryption (has to be configured in `~/.gnupg/gpg.conf`). Optional.

- `encfs_password`: password to use for encrypted filesystem. By default it will be sent to encfs via stdin, and it will be visible in process list accessible for example by `ps` and in Ansible log files. Optional, required for encryption on remote hosts.

- `encfs_passfile`: absolute path to a file on remote host which will hold password defined in `encfs_password` during transit to EncFS, thus avoiding the exposure in process list and Ansible logs. Role creates two files with suffixes `_init` and `_pass` and shreds them when they are no longer needed. Optional.

- `encfs_mode`: by default 'encfs' role behaves as a toggle - opens encrypted filesystem if it's closed, closes it when opened. Using this variable you can force a particular mode of operation - "open" opens the encrypted filesystem, "close" closes it. Useful with `--extra-vars`. Optional.

- `encfs_random`: device that will be used to get randomness from, `/dev/random` by default. You might want to switch it to `/dev/urandom` on development/testing hosts to speed up certain operations. Optional.

Usage
-----

To use 'encfs' role for encrypted storage for all your hosts, you should set at least one variable (for example `secret`) in `inventory/group_vars/all.yml` which will point to a directory in your local filesystem. By default, 'encfs' will create an keyfile and encrypt it using a GPG passphrase. To change how 'encfs' behaves, in `inventory/host_vars/localhost.yml` set variables like `encfs_gpg`, `encfs_password`, `encfs_passfile` (described above). This way the scope of the `encfs_*` variables will be limited only to `localhost`.

You have to add 'localhost' to your inventory, preferably at the begginning of the `hosts` file, like this:

    localhost ansible_connection=local

Add two plays at the beginning and end of your playbook, like this:

    ---
    - hosts: localhost
      sudo: no
      roles:
        - role: encfs
          encfs: '{{ secret }}'
          encfs_mode: 'open'
    
    - hosts: all:!localhost
      # your plays here
    
    - hosts: localhost
      sudo: no
      roles:
        - role: encfs
          encfs: '{{ secret }}'
          encfs_mode: 'close'

When you will run a playbook modified as above for the first time, Ansible might require `sudo` access to install 'fuse' and 'encfs' packages, fix `/dev/fuse` access permissions and add your user to 'fuse' group. If that happens, 'encfs' role will stop playbook and inform you that you need to log out and back in to have 'fuse' group available.

Another way to use 'encfs' role for encrypted global storage is to create a shell script, and run that role using separate `ansible-playbook` commands. Here's an example script:

    #!/bin/bash
    
    if [ $SECRET -gt 0 ] ; then
    	ansible-playbook -i inventory playbooks/secret.yml --extra-vars='encfs_mode=open'
    	trap "ansible-playbook -i inventory playbooks/secret.yml --extra-vars='encfs_mode=close'" EXIT
    fi
    
    ansible-playbook -i inventory playbooks/site.yml $@

And in `playbooks/secret.yml` you should create a playbook:

    - hosts: localhost
      sudo: no
      roles:
        - role: encfs
          encfs: '{{ secret }}'

When you run that script, you can specify `ansible-playbook` options as normal, and they will be used with correct command. When last of your plays finishes, shell script will run Ansible with `encfs` role again, to close encrypted filesystem.

License
-------

GPLv3

Author Information
------------------

Written by: [Maciej Delmanowski](http://twitter.com/drybjed). Part of the [ginas](https://github.com/ginas/) project.

