.. _debops.yadm:

debops.yadm
===========

`Yet Another Dotfiles Manager`__ (:command:`yadm`) is a wrapper script around
the :command:`git` command that manages `dotfiles`__ located in the ``$HOME``
directory using a :command:`git` repository. yadm supports encrypted storage
for sensitive files, alternative file selection based on host
class/OS/hostname/user account, bootstrap script and Jinja templating.

.. __: https://yadm.io/

.. __: https://en.wikipedia.org/wiki/Hidden_file_and_hidden_directory

The ``debops.yadm`` Ansible role will install the :command:`yadm` script,
either from an APT repository, or using the upstream :command:`git` repository.
The role will also install a ``zsh`` shell and a few essential CLI
applications.

Optionally, ``debops.yadm`` role can clone selected dotfiles :command:`git`
repositories to the host creating mirrors, that can be used by users or other
Ansible roles to deploy dotfiles locally.


.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.yadm/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
