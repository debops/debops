.. Copyright (C) 2016      Mariano Barcia <mariano.barcia@gmail.com>
.. Copyright (C) 2016-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.php`` role can be used to manage PHP Hypertext Preprocessor
environment on a Debian/Ubuntu host. The role supports different PHP versions
available in OS distributions (PHP5, PHP7) with PHP-FPM service and multiple
PHP-FPM pools. Other Ansible roles can use it as a role dependency to offload
PHP management for their own use.
