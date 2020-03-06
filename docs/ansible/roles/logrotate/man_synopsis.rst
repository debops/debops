.. Copyright (C) 2016-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops service/logrotate`` [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags** `tag1,tag2,`...] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops`` **--tags** ``role::logrotate`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops`` **--skip-tags** ``skip::logrotate`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...
