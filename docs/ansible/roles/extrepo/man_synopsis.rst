.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Synopsis
========

``debops service/extrepo`` [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags** `tag1,tag2,`...] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops`` **--tags** ``role::extrepo`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops`` **--skip-tags** ``skip::extrepo`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...
