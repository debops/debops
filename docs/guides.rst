Detailed guides
===============

How local secrets work
----------------------

Here's a default project directory layout kept in a git repository::

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

If you use ``debops-padlock`` script to create encrypted EncFS storage for your
secrets, directory layout will be slightly different::

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
they don't show up in the ``secret/`` directory. When you use ``debops`` script to
run the playbook, ``padlock`` script unlocks the encrypted directory and secrets
are available again in ``secret/`` directory for ``ansible-playbook`` to use.

