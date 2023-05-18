.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

The `apt-mirror`__ script can be used to create full or partial mirrors of APT
repositories. It uses syntax similar to the :man:`sources.list(5)`
configuration file, supports authenticated APT repositories, access over HTTPS
and more.

.. __: https://apt-mirror.github.io/

The :ref:`debops.apt_mirror` role can be used to install and configure the
``apt-mirror`` script to periodically pull different APT repositories and
publish them using :command:`nginx` for other hosts to use. The role supports
configuration of multiple mirror "instances", which can be configured with
different mirror frequency as needed.
