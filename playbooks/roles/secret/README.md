secret
======

Ansible role `secret` allows you to store and update passwords, certificates and other sensitive data in a secure way. To achieve this, `secret` uses `cryptsetup` command and [LUKS](https://en.wikipedia.org/wiki/Linux_Unified_Key_Setup) to create encrypted storage file with configurable size, protected by a keyfile encrypted with GnuPG, either using symmetric encryption with a passphrase, or OpenPGP public key encryption with one or multiple GnuPG keys.

**Warning:** Due to the way `secret` role is constructed, passwords and other sensitive data stored in Ansible variables might leak during Ansible execution, potentially in system process list accessed for example with `ps` command, or in log files written by Ansible scripts on local and remote hosts. When solution to these problems is found, it will be implemented in the `secret` role as soon as possible.

Requirements
------------

- `sudo` access on localhost will be required to mount LUKS device and format it using ext2 filesystem.

- `gpg` will be used to encrypt keyfile for encrypted storage file, either with a passphrase or provided GPG key.

- `cryptsetup` will be installed on Debian/Ubuntu systems if it's not present.

Role Variables
--------------

- `secret`: **absolute path to a directory in your local filesystem**. It has to exist, and your user should have access rights. It will be used as a mount point for encrypted storage while it is opened, so use empty directory and avoid putting it in place that might change during playbook execution. Mandatory.

- `secret_gpg`: list of one or more OpenPGP public keys to use for encryption. If this variable is not defined in inventory, GnuPG will ask for a passphrase during storage creation and every time encrypted storage is opened; with OpenPGP keys GnuPG can utilize `gpg-agent` for decryption (has to be configured in `~/.gnupg/gpg.conf`). Optional.

- `secret_size`: size of encrypted storage in MB. By default, 64 MB. Optional.

- `secret_random`: device that will be used to get randomness from, `/dev/random` by default. You might want to switch it to `/dev/urandom` on development/testing hosts to speed up certain operations. Optional.

Usage
-----

Add two plays at the beginning and end of your playbook, like this:

    ---
    - hosts: localhost
      sudo: no
      roles:
        - { role: secret, secret_mode: 'open' }
    
    - hosts: all:!localhost
      # your plays here
    
    - hosts: localhost
      sudo: no
      roles:
        - { role: secret }

This way, Ansible will use `secret` role to create and/or open secret storage, run your playbooks and close secret storage at the end (during execution, files inside secret storage will be mounted in place of `secret` directory with owner and group of your user and `0700` permissions). This method has a disadvantage - when you use `ansible-playbook` command, you need to specify `--limit group,localhost` each time, or `secret` role will not be executed by Ansible.

Another way to use `secret` role is to create a shell script, and run that role using separate `ansible-playbook` command. Here's an example script:

    #!/bin/sh
    
    if [ -z "${TOO_MANY_SECRETS}" ] ; then
    	ansible-playbook -i inventory playbooks/secret.yml --extra-vars="secret_mode=open"
    	trap "ansible-playbook -i inventory playbooks/secret.yml" EXIT
    fi
    
    ansible-playbook -i inventory playbooks/site.yml $@

And in `playbooks/secret.yml` you should create a playbook:

    - hosts: localhost
      sudo: no
      roles:
        - { role: secret }

When you run that script, you can specify `ansible-playbook` options as normal, and they will be used with correct command. When last of your plays finishes, shell script will run Ansible with `secret` role again, to close secret storage.

### Example usage - password lookup

Create a variable in your inventory or role defaults, `example_password` with default password you want to be assigned. In your playbook/role, before you use that password, add a task:

    - name: Lookup password in secret/ directory
      set_fact:
        example_password: "{{ lookup('password', secret + '/credentials/' + ansible_fqdn + '/role/password_file' }}"
      when: secret is defined and secret

Now you can use `'{{ example_password }}'` variable in your subsequent tasks or templates; if `secret` directory is defined, your password will be saved in encrypted storage, if it's not, your task/role will use default password defined in inventory or defaults. Password will be saved in `'{{ secret }}/credentials/{{ ansible_fqdn }}/role/password_file'`. Make sure to use `{{ ansible_fqdn }}` variable or other variable that specifies individual hosts in your playbook, to have separate passwords for each host. Or, use path without it to have the same password on different hosts.

### Example usage - file management

Here are example tasks which can be used to fetch files from remote hosts and copy them to remote hosts:

    - name: Fetch /etc/fstab and store it securely
      fetch: flat=yes src=/etc/fstab
             dest={{ secret }}/storage/{{ ansible_fqdn }}/etc/fstab
      when: secret is defined and secret
    
    - name: Copy /etc/fstab from secure storage
      copy: src={{ secret }}/storage/{{ ansible_fqdn }}/etc/fstab
            dest=/etc/fstab owner=root group=root mode=0644
      when: secret is defined and secret


Detailed Description
--------------------

Role `secret` is meant to be run on `localhost` (Ansible controller), on local user account. Ansible will issue `sudo` commands directly when needed, to not interfere with requirements of main playbook.

On the first run, a random string (LUKS passphrase) is piped through `gpg`, encrypted and saved in a separate "keyfile" to be used later. Next, a storage space with random contents is created in directory specified in `secret` variable, using `dd`. `cryptsetup` command creates new LUKS device and encrypts it using LUKS passphrase decrypted with `gpg`. Then, encrypted device is formatted using EXT2 filesystem (journal is not required). After that, encrypted device (`/dev/mapper/*` is mounted with `-o bind` option in `secret` directory, essentially "replacing" encrypted file with it's contents, from the point of view of Ansible. When main playbook is finished, `secret` role is run again, but this time it will only unmount and close the encrypted device, leaving the keyfile and image file in the `secret` directory.

On subsequent runs the process is repeated, but without generating and encrypting new files - Ansible decrypts the image file using LUKS passphrase from keyfile decrypted using `gpg`, opens LUKS encrypted device and mounts it's contents in `secret` directory, leaving it accessible to the main playbook. At the end, directory is unmounted and LUKS device is closed.

License
-------

GPLv3

Author Information
------------------

Written by: [Maciej Delmanowski](http://twitter.com/drybjed). Part of the [ginas](https://github.com/ginas/) project

