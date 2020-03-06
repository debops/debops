.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016      Patrick Heeney <patrickheeney@gmail.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Node.js`__ is a JavaScript runtime environment which can be used to execute JS
code outside of the browser. It is commonly used for server-side applications
written in JavaScript.

.. __: https://nodejs.org/

There are two popular package managers in the Node.js ecosystem: `NPM`__ which
is bundled with Node.js, and `Yarn`__, a third-party package manager that is
compatible with NPM.

.. __: https://npmjs.org/
.. __: https://yarnpkg.org/

The ``debops.nodejs`` Ansible role can be used to manage a Node.js environment
on a host. By default, it will install Node.js, NPM and Yarn packages included
in a given OS release (if possible), but it can also automatically install or
upgrade an existing installation to their upstream versions.
