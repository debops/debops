.. Copyright (C) 2013-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2016 Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops service/ferm`` [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags** `tag1,tag2,`...] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops`` **--tags** ``role::ferm`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops`` **--skip-tags** ``skip::ferm`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...
