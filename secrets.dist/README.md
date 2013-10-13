## Example secrets/ directory for Ansible

Using this directory, you can keep files that you don't want to be publicly available to use in Ansible (for example certificate keys, passwords, etc.).

It's best to have that directory in a separate git repository and use it as an absolute path in your plays / variables. To use it in `ansible-aiua`, set a variable in `inventory/group_vars/all`:

    ---
    secret: '/absolute/path/to/secrets'

After that, roles that use secret files will be able to use that directory ([an example of that usage](https://github.com/drybjed/ansible-aiua/blob/master/playbooks/roles/mysql/tasks/main.yml#L32-L55) can be found in `playbooks/roles/mysql/tasks/main.yml`).

