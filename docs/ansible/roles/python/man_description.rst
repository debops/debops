.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Python`__ is a popular, dynamic programming language available on GNU/Linux
platforms. Ansible is written in Python and requires Python on remote host for
normal operations.

.. __: https://www.python.org/

The ``debops.python`` Ansible role can be used to manage the Python environment
on a Debian/Ubuntu host. Role supports multiple Python versions installed on
a host at the same time, which is the default practice in Debian.

A special "raw" mode of operation with a separate Ansible playbook can be used
to bootstrap Python environment on a host, so that Ansible can then install
packages and operate normally.
