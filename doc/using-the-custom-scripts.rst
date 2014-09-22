Using the custom scripts
========================

- `Where were they installed to?`_
- `debops-update`_
- `debops-init`_
- `debops-task`_
- `debops`_
- `debops-padlock`_

Where were they installed to?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you allowed them to be installed on your system path then they will be in
``/usr/local/bin`` and directly accessible.

****

debops-update
^^^^^^^^^^^^^

Updates the playbooks and roles relative to ``$PWD``, if none are found
then it will update them at their default location.

****

debops-init
^^^^^^^^^^^

Creates a project for you at the path you specify. After running this script
you should check out ``ansible/inventory/hosts`` relative to your project path.

::

    debops-init ~/myproject

****

debops-task
^^^^^^^^^^^

Wraps ``ansible``, it can accept anything ``ansible`` does.

You could use it to run adhoc tasks against your hosts.

::

    debops-task all -m setup

    debops-task somegroup -m shell "touch /tmp/foo && rm -rf /tmp/foo"

****

debops
^^^^^^

Wraps ``ansible-playbook`` and since that's the most commonly ran command we
decided it's a good idea to shorten it to ``debops`` instead of ``debops-playbook``.

Any arguments that ``ansible-playbook`` supports can be passed to ``debops``.

You don't need to specify an inventory or playbook. Part of the benefit of
using this tool is that it figures out all of that stuff for you. You can still
chain together multiple playbooks, custom or not.

::

    debops -l mygroup

    debops -t foo

debops-padlock
^^^^^^^^^^^^^^

An optional script that allows you to encrypt your secrets directory using
EncFS and GPG.

1. Make sure you have encfs installed, ie. ``apt-get install encfs``
2. Make sure you have a `GPG keypair <https://alexcabal.com/creating-the-perfect-gpg-keypair/>`_
3. Make sure ``$project_dir/ansible/secret/`` is empty
4. Run ``debops-padlock`` and enter your GPG password unless you have an agent
5. Goto ``$project_dir/ansible/.encfs.secret/``
6. Run ``./padlock unlock``
7. Do something that would result in adding files to ``secret/``, such as touching a file
8. Run ``./padlock lock``
9. Confirm you have 1 or more sub-folders or files in ``.encfs.secret/``

The above steps performed the following tasks:

- Setup a project directory to use an encrypted secrets directory
- Added files to be encrypted
- Locked it, which unmounts ``secret/`` -- it is now secure

That sounds annoying, can it be done better?
--------------------------------------------

When running any play book through the ``debops`` script, it will automatically
take care of unlocking/locking it after the run finishes successfully or errors out.

There is a catch, make sure you always use ``debops`` to run your plays because
if you run ``ansible-playbook`` directly the unlock/lock process will not
happen automatically. It may change your passwords and whatever else you have stored.

If you use the ``debops`` script you won't have to worry about anything being changed.

Delete your secrets
-------------------

Since EncFS mounts ``secret/`` you need to unlock it first. If you
forgot to unlock it first then you will get a device is busy error.

You can fix this by unmounting it yourself before trying to delete it, run:

``fusermount -u <path to secret/>``

Migrate an existing secrets directory to be encrypted
-----------------------------------------------------

EncFS can only mount empty directories but don't worry. Just move the files
inside of ``secret/`` to somewhere else, then start the steps above.

Why does it ask for the GPG password twice?
-------------------------------------------

2 files are being encrypted. The EncFS configuration and the EncFS keyfile.
If you use an agent then you won't have to enter your password.

What if GPG fails to decrypt?
-----------------------------
If the configuration is not decrypted properly, EncFS discards the garbled data
and tries to create a new encrypted directory. You can just ``CTRL+C`` to
quit and fix your issues.
