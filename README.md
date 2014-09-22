
## [![DebOps project](http://debops.org/images/debops-small.png)](http://debops.org) secret



[![Travis CI](http://img.shields.io/travis/debops/ansible-secret.svg?style=flat)](http://travis-ci.org/debops/ansible-secret) [![test-suite](http://img.shields.io/badge/test--suite-ansible--secret-blue.svg?style=flat)](https://github.com/debops/test-suite/tree/master/ansible-secret/)  [![Ansible Galaxy](http://img.shields.io/badge/galaxy-debops.secret-660198.svg?style=flat)](https://galaxy.ansible.com/list#/roles/1598) [![Platforms](http://img.shields.io/badge/platforms-debian%20|%20ubuntu-lightgrey.svg?style=flat)](#)






This role enables you to have a separate directory on Ansible Controller
(different than the playbook directory and inventory directory) which can be
used as a handy "workspace" for other roles.

Some usage examples of this role in [DebOps](http://debops.org/)
include:

- password lookups, either from current role, or using known location of
  passwords from other roles, usually dependencies (for example 'mysql' role
  can manage an user account in the database with random password and other
  role can lookup that password to include in a generated configuration file);

- secure file storage, for example for application keys generated on remote
  hosts ('boxbackup' role retrieves client keys for backup purposes), for
  that reason secret directory should be protected by an external means, for
  example encrypted filesystem (currently there is no encryption provided by
  default);

- secure workspace ('boxbackup' role, again, uses secret directory to create
  and manage Root CA for backup servers - client and server certificates are
  automatically downloaded to Ansible Controller, signed and uploaded to
  destination hosts);

- simple centralized backup (specific roles like 'sshd', 'pki' and
  'monkeysphere' have a separate task lists that are invoked by custom
  playbooks to allow backup and restoration of ssh host keys and SSL
  certificates. Generated .tar.gz files are kept on Ansible Controller in
  secret directory);





### Installation

This role requires at least Ansible `v1.7.0`. To install it, run:

    ansible-galaxy install debops.secret

#### Are you using this as a standalone role without DebOps?

You may need to include missing roles from the [DebOps common
playbook](https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml)
into your playbook.

[Try DebOps now](https://github.com/debops/debops) for a complete solution to run your Debian-based infrastructure.








### Role variables

List of default variables available in the inventory:

    ---
    
    # Path to a directory in which a relative secret directory will be created.
    # By default, it will be relative to Ansible inventory
    secret_root: '{{ inventory_dir | realpath }}'
    
    # Name of the directory which contains secrets. It will be in the form
    # "secret" by default
    secret_dir: 'secret'
    
    # How many directory levels to add relative to secret_root, by default 1 level.
    # For example, to go 2 levels up, set this variable to '../..'
    secret_levels: '..'
    
    # Absolute path to directory with secrets. It will be configured as relative to
    # current inventory directory. Use this variable in file and password lookups
    secret: '{{ secret_root + "/" + secret_levels + "/" + secret_dir }}'






### Detailed usage guide

Here's a default project directory layout kept in a git repository:

    ~/Projects/
    `-- data-center/
        |-- .git/
        `-- ansible/
            |-- inventory/
            |   |-- group_vars/
            |   |-- host_vars/
            |   `-- hosts
            |
            `-- secret/
                |-- credentials/
                `-- storage/

If you use `debops-padlock` script to create encrypted EncFS storage for your
secrets, directory layout will be slightly different:

    ~/Projects/
    `-- data-center/
        |-- .git/
        `-- ansible/
            |-- .encfs.secret/        <- encrypted secrets
            |   |-- U8dfMgfgg48vj/
            |   |-- fk5fkg5NN/
            |   `-- padlock*          <- unlock/lock script
            |
            |-- inventory/
            |   |-- group_vars/
            |   |-- host_vars/
            |   `-- hosts
            |
            `-- secret/               <- plaintext secrets

While project is "at rest", secrets are encrypted inside EncFS directory, and
they don't show up in the `secret/` directory. When you use `debops` script to
run the playbook, `padlock` script unlocks the encrypted directory and secrets
are available again in `secret/` directory for `ansible-playbook` to use.

#### Support for --tags

By default all you need to do to use 'secret' role is include it in your common
playbook at the beginning:

    ---
    - hosts: all
      roles:
        - role: debops.secret

That will allow all your roles in this and subsequent plays to access `secret`
variable and use it consistently.

Unfortunately, it doesn't work well when you use Ansible with `--tags`
parameter, which might omit your common play, thus not setting `secret`
variables at all and changing your passwords to empty values, modifying config
files incorrectly, basically not honoring the idempotency principle.

Solution to that problem is to either include 'secret' role in all your plays
(similar to the one above), or include it as a dependency in roles that require
it:

    ---
    dependencies:
      - role: debops.secret

This will ensure that roles utilizing `secret` variable will be able to access
it correctly and you don't need to remember to include 'secret' role in all
your playbooks.


#### Usage examples

Example password lookup with password written to a variable. You can define
this variable anywhere Ansible variables can be defined, but if you want to
give playbook users ability to overwrite it in inventory, you should define it
in `role/defaults/main.yml`:

    ---
    mysql_root_password: "{{ lookup('password', secret + '/credentials/' + ansible_fqdn + '/mysql/root/password') }}"

When this variable is set in `role/defaults/main.yml`, you can easily overwrite
it in your inventory, like this:

    ---
    mysql_root_password: "correct horse battery staple"

You can also change the password directly in secret directory, in this case in
`secret/credentials/hostname/mysql/root/password` and Ansible should update the
password on the remote server (if role is written to support this).

Example file download task from remote host to Ansible controller, sored in
secret directory:

    ---
    fetch: src=/etc/fstab flat=yes
           dest="{{ secret + '/storage/' + ansible_fqdn + '/etc/fstab' }}"

Example file upload task from Ansible Controller to remote host with file from
secret directory:

    ---
    copy: dest=/etc/fstab owner=root group=root mode=0644
          src="{{ secret + '/storage/ + ansible_fqdn + '/etc/fstab' }}"






### Authors and license

`secret` role was written by:

- Maciej Delmanowski | [e-mail](mailto:drybjed@gmail.com) | [Twitter](https://twitter.com/drybjed) | [GitHub](https://github.com/drybjed)

License: [GPLv3](https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29)



***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).
