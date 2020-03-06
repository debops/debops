.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops service/ldap`` [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags** `tag1,tag2,`...] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops`` **--tags** ``role::ldap`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops`` **--tags** ``role::ldap:tasks`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [<``ansible-playbook`` options>] ...

``debops`` **--skip-tags** ``skip::ldap`` [`playbook`] ... [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...
