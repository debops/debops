secret
======

This is a small wrapper role around 'encfs' role, which allows you to manage secret storage space on Ansible Controller.

Requirements
------------

The same as 'encfs' role.

Role Variables
--------------

- `secret`: **absolute path to a directory in your local filesystem**. It has to exist, and your user should have access rights. It will be used as a mount point for encrypted storage while it is opened, so use empty directory and avoid putting it in place that might change during playbook execution. Mandatory.

Other useful variables can be found in 'encfs' role.

Usage
-----

Set `secret` variable in `inventory/group_vars/all.yml` to have consistent path to secret storage in all parts of your playbook. After that, when you use '{{ secret }}' as a part of the path to files you copy, template or lookup using Ansible, Ansible will look for them in the directory you specified earlier, which will be decrypted during playbook run.

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

License
-------

GPLv3

Author Information
------------------

Written by: [Maciej Delmanowski](http://twitter.com/drybjed). Part of the [ginas](https://github.com/ginas/) project.

