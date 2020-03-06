.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Imre Jonk <mail@imrejonk.nl>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.docker_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation
and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _docker_server__ref_pip_packages:

docker_server__pip_packages
---------------------------

The :envvar:`docker_server__default_pip_packages` and
:envvar:`docker_server__pip_packages` list variables define what PyPI packages
will be installed in the Python virtualenv environment controlled by the
``debops.docker_server`` role. You can specify either package names as string,
or YAML dictionaries with specific parameters:

``name``
  Required. The name of the PyPI package to install.

``version``
  Optional. If specified, install the specified version of the PyPI package
  instead of the latest one.

``state``
  Optional. If not specified or ``present``, the package will be installed in
  the Python virtualenv. If ``absent``, the package will be removed from the
  Python virtualenv.

``path`` and ``src``
  Optional. If specified together, the role will create a symlink at the
  ``path`` location (should specify an absolute path) to the ``src`` file or
  directory.

For example usage, see the default variables mentioned above.
