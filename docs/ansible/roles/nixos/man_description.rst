.. Copyright (C) 2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

`NixOS`__ is a Linux-based operating system which uses a functional programming
language, `Nix`__, to control the state of the whole system. NixOS is built
from the ground up on an idea of configuration management being the only method
to configure the system. It's an alternative to Ansible and allows for unique
capabilities like whole-system rollbacks, immutability, ability to install
multiple versions of a given software side by side, and other functionality not
available or hard to achieve on traditional Linux distributions.

The :ref:`debops.nixos` role can be used to distribute Nix configuration files
to NixOS-based remote hosts using Ansible. This provides an alternative method
of managing multiple NixOS hosts and allows easy integration with Debian/Ubuntu
hosts managed by Ansible and/or DebOps.

.. __: https://nixos.org/
.. __: https://nix.dev/
