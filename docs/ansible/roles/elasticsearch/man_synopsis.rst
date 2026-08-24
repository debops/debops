.. Copyright (C) 2014-2016 Nick Janetakis <nick.janetakis@gmail.com>
.. Copyright (C) 2014-2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016      Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2014-2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Synopsis
========

``debops run service/elasticsearch`` [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags** `tag1,tag2,`...] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops run scope/elasticsearch`` [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags** `tag1,tag2,`...] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...

``debops run scope/elasticsearch/remove_node`` [**--limit** `group,host,`...] [**--diff**] [**--check**] [**--tags** `tag1,tag2,`...] [**--skip-tags** `tag1,tag2,`...] [<``ansible-playbook`` options>] ...
