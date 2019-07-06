Default variable details
========================

Some of ``debops.yadm`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _yadm__ref_dotfiles:

yadm__dotfiles
--------------

The ``yadm__*_dotfiles`` variables define a list of custom dotfile
:command:`git` repositories to clone to the host, so that they are available
locally. The dotfiles will be cloned to the directory defined by the
:envvar:`yadm__dotfiles_root` variable, with subdirectories corresponding to
the repository host (for example ``github.com``), repository owner (for example
``drybjed``), and finally the ``dotfiles.git`` directory, which contains a bare
:command:`git` repository itself.

The repositories are cloned and/or updated using the ``root`` account, with
optional GPG signature verification. The role does not execute any code
contained in the repositories at this stage. Users are then able to use the
:command:`yadm` script to install or update their desired dotfiles from the
local mirror instead of the remote repository. This can be done either
manually, or via other Ansible roles.

Because :command:`yadm` uses the ``$HOME`` directory directly as the
:command:`git` work directory, it's best to avoid putting non-dotfile files
like ``README.md`` and similar in the ``master`` branch of the repository
(:command:`yadm` will check it out by default). If you want to present a README
file in the dotfiles repository, you can put it on a separate :command:`git`
branch and set it as default branch in the GitHub repository settings.

See `yadm dotfile repository examples`__ for an example repositories compatible
with :command:`yadm` script.

.. __: https://yadm.io/docs/examples

Examples
~~~~~~~~

Clone dotfiles without any GPG signature verification:

.. code-block:: yaml

   yadm__dotfiles:

     - name: 'user'
       git:
         - repo: 'https://github.com/user/dotfiles'

Disable the default ``drybjed`` dotfiles from being cloned automatically and
remove them if they are present:

.. code-block:: yaml

   yadm__dotfiles:

     - name: 'drybjed'
       state: 'absent'

Syntax
~~~~~~

The variables are YAML lists, each list entry is a YAML dictionary that uses
specific parameters:

``name``
  Required. A name of a given dotfile entry, not used otherwise. Entries with
  the same ``name`` parameter are merged together, this can be used to modify
  existing entries later on.

``state``
  Optional. If not specified or ``present``, a given dotfile repository will be
  cloned or updated by the role. If ``absent``, a given repository and GPG keys
  will be removed from the host, or will not be imported and cloned. If
  ``ignore``, a given configuration entry will be ignored during evaluation by
  the role.

``gpg``
  Optional. A string containing a GPG key fingerprint used to sign the commits
  and/or tags in the dotfile repository; you can also specify multiple GPG
  fingerprints as a YAML list. Spaces in the fingerprint will be automatically
  removed. An alternative format is a YAML dictionary for each list element,
  with specific parameters:

  ``id``
    The GPG key fingerprint.

  ``keybase``
    Optional. The name of the `Keybase`__ profile which should be used to
    lookup the GPG key.

    .. __: https://keybase.io/

  ``state``
    Optional, either ``present`` (import the GPG key) or ``absent`` (remove the
    GPG key from the keyring).

  The specified GPG keys will be added to the ``root`` GPG keyring in the
  :file:`~/.gnupg/pubring.gpg` file and subsequently used to verify commits in
  cloned or updated :command:`git` repositories.

  The GPG keys are managed via the :ref:`debops.keyring` Ansible role, see its
  documentation for more details.

``git``
  Optional. A string containing an URL to the :command:`git` repository with
  dotfiles; you can also specify multiple URLs as a YAML list. Only public
  repositories accessible via ``https://`` make sense - the role does not
  support cloning private repositories using a password, or repositories
  accessible over SSH connection. An alternative format is a YAML dictionary
  for each list element, with specific parameters:

  ``repo``
    The URL of the repository.

  ``version``
    The :command:`git` branch/tag to checkout - not useful because the role
    will clone bare :command:`git` repositories without checking them out.
