# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014, Christian Berendt <berendt@b1-systems.de>
# Copyright (C) 2022 Julien Lecomte <julien@lecomte.at>
# Copyright (C) 2022 DebOps <https://debops.org/>
# SPDX-License-Identifier:  GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re

# import module snippets
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: apache2_module
author:
    - Christian Berendt (@berendt)
    - Ralf Hertel (@n0trax)
    - Robin Roth (@robinro)
    - Julien Lecomte
short_description: Enables/disables a module of the Apache2 webserver.
description:
   - Enables or disables a specified module of the Apache2 webserver.
options:
   name:
     type: str
     description:
        - Name of the module to enable/disable as given to C(a2enmod/a2dismod).
     required: true
   identifier:
     type: str
     description:
        - Deprecated. Ignored.
     required: False
   force:
     description:
        - Force disabling of default modules and override Debian warnings.
     required: false
     type: bool
     default: False
   state:
     type: str
     description:
        - Desired state of the module.
     choices: ['present', 'absent']
     default: present
   ignore_configcheck:
     description:
        - Deprecated. Ignored.
     type: bool
     default: False
requirements: ["a2enmod","a2dismod"]
notes:
  - This does not work on RedHat-based distributions.
    Whether it works on others depend on whether the C(a2enmod), C(a2dismod),
    and C(a2query) tools are available or not.
'''

EXAMPLES = '''
- name: Enable the Apache2 module wsgi
  community.general.apache2_module:
    state: present
    name: wsgi

- name: Disables the Apache2 module wsgi
  community.general.apache2_module:
    state: absent
    name: wsgi

- name: Disable default modules for Debian
  community.general.apache2_module:
    state: absent
    name: autoindex
    force: True
'''

RETURN = '''
result:
    description: message about action taken
    returned: always
    type: str
warnings:
    description: list of warning messages
    returned: when needed
    type: list
rc:
    description: return code of underlying command
    returned: failed
    type: int
stdout:
    description: stdout of underlying command
    returned: failed
    type: str
stderr:
    description: stderr of underlying command
    returned: failed
    type: str
'''

_re_threaded = re.compile(r'threaded: *yes')


def _run_threaded(module):
    control_binary = _get_ctl_binary(module)
    result, stdout, stderr = module.run_command([control_binary, "-V"])

    return bool(_re_threaded.search(stdout))


def _get_ctl_binary(module):
    ctl_binary = module.get_bin_path('a2query')
    if ctl_binary is not None:
        return ctl_binary

    module.fail_json(msg="a2query not found. Apache query binary is necessary.")


def _module_is_enabled(module):
    control_binary = _get_ctl_binary(module)
    result, stdout, stderr = module.run_command([control_binary,
                                                "-m", module.params['name']])

    if result in [0, 1, 32]:
        return result == 0
    else:
        error_msg = "Error executing %s: %s" % (control_binary, stderr)
        module.fail_json(msg=error_msg)


def _set_state(module, state):
    name = module.params['name']
    force = module.params['force']

    want_enabled = state == 'present'
    state_string = {'present': 'enabled', 'absent': 'disabled'}[state]
    a2mod_binary = {'present': 'a2enmod', 'absent': 'a2dismod'}[state]
    success_msg = "Module %s %s" % (name, state_string)

    module.run_command_environ_update = dict(LANG='C', LC_ALL='C',
                                             LC_MESSAGES='C', LC_CTYPE='C')

    if module.check_mode:
        enabled_state = _module_is_enabled(module)
        module.exit_json(changed=(enabled_state == want_enabled),
                         result=success_msg,
                         warnings=module.warnings)

    a2mod_binary_path = module.get_bin_path(a2mod_binary)
    if a2mod_binary_path is None:
        module.fail_json(msg="%s not found."
                         + " "
                         + "Perhaps this system does not use %s to manage apache"
                         % (a2mod_binary, a2mod_binary))

    a2mod_binary_cmd = [a2mod_binary_path]

    if not want_enabled and force:
        # force exists only for a2dismod on debian
        a2mod_binary_cmd.append('-f')

    result, stdout, stderr = module.run_command(a2mod_binary_cmd + [name])

    if result == 0:
        module.exit_json(changed=(' already ' not in stdout),
                         result=success_msg,
                         warnings=module.warnings)
    else:
        msg = (
            'Failed to set module {name} to {state}:\n'
            '{stdout}\n'
        ).format(
            name=name,
            state=state_string,
            stdout=stdout,
        )
        module.fail_json(msg=msg,
                         rc=result,
                         stdout=stdout,
                         stderr=stderr)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            force=dict(type='bool', default=False),
            state=dict(default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True,
    )

    module.warnings = []

    name = module.params['name']
    if name == 'cgi' and _run_threaded(module):
        module.fail_json(msg="Your MPM seems to be threaded."
                         + " "
                         + "No automatic actions on module cgi possible.")

    if module.params['state'] in ['present', 'absent']:
        _set_state(module, module.params['state'])


if __name__ == '__main__':
    main()
