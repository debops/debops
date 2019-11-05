.. _cmd_debops-padlock:

The :command:`debops-padlock` command
=====================================

.. include:: ../../includes/global.rst

An optional script that allows you to encrypt your secrets directory using
EncFS and GPG.

1. Make sure you have encfs installed, ie. ``apt-get install encfs``
2. Make sure you have a `GPG keypair <https://alexcabal.com/creating-the-perfect-gpg-keypair/>`_
3. Make sure :file:`$project_dir/ansible/secret/` is empty
4. Run ``debops-padlock init`` and enter your GPG password unless you
   have an agent
5. Run ``debops-padlock unlock``
6. Do something that would result in adding files to :file:`secret/`, such
   as touching a file
7. Run ``debops-padlock lock``
8. Confirm you have 1 or more sub-folders or files in :file:`.encfs.secret/`

The above steps performed the following tasks:

- Setup a project directory to use an encrypted secrets directory
- Added files to be encrypted
- Locked it, which unmounts :file:`secret/` -- it is now secure


That sounds annoying, can it be done better?
--------------------------------------------

When running any play book through the ``debops`` script, it will automatically
take care of unlocking/locking it after the run finishes successfully or errors out.

There is a catch, make sure you always use ``debops`` to run your plays because
if you run :command:`ansible-playbook` directly the unlock/lock process will not
happen automatically. It may change your passwords and whatever else you have stored.

If you use the ``debops`` script you won't have to worry about anything being changed.


Delete your secrets
-------------------

Since EncFS mounts :file:`secret/` you need to unlock it first. If you
forgot to unlock it first then you will get a device is busy error.

You can fix this by unmounting it yourself before trying to delete it, run:

``fusermount -u <path to secret/>``


Migrate an existing secrets directory to be encrypted
-----------------------------------------------------

EncFS can only mount empty directories but don't worry. Just move the files
inside of :file:`secret/` to somewhere else, then start the steps above.


Why does it ask for the GPG password twice?
-------------------------------------------

Two files are being encrypted. The EncFS configuration and the EncFS keyfile.
If you use an agent then you won't have to enter your password.


What if GPG fails to decrypt?
-----------------------------

If the configuration is not decrypted properly, EncFS discards the garbled data
and tries to create a new encrypted directory. You can just ``CTRL+C`` to
quit and fix your issues.


What if you want to keep your encrypted secrets in a git repository?
--------------------------------------------------------------------

DebOps by default creates an entry in ``.gitignore`` file to prevent committing
encrypted files to the git repository. If you are sure that you want to do it,
just comment or remove the `.encfs.secret` line from ``.gitignore``.

You can also use :ref:`debops.secret` role to keep the content of the
:file:`secret/` directory in other sorts of storage -
for details please consult the documentation of that role.


..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
