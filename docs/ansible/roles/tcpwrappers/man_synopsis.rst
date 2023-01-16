.. Copyright (C) 2014-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2016 DebOps <http://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops run service/tcpwrappers`` [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags** `tag1,tag2,`...] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops run site`` **--tags** ``role::tcpwrappers`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops run site`` **--skip-tags** ``skip::tcpwrappers`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...
