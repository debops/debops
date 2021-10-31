#!/usr/bin/env python
# -*- coding: utf-8 -*-

# cran.py: install or remove R packages
# Homepage: https://github.com/yutannihilation/ansible-module-cran

# Copyright (C) 2016 Hiroaki Yutani <yutani.ini@gmail.com>
# Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017 DebOps <https://debops.org/>
# SPDX-License-Identifier: MIT

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: cran
short_description: Install R packages.
options:
  name:
    description:
      - The name of an R package.
    required: true
    default: null
  state:
    description:
      - The state of module
    required: false
    choices: ['present', 'absent']
    default: present
  repo:
    description:
      - The repository
    required: false
    default: "https://cran.rstudio.com/"
'''

RSCRIPT = '/usr/bin/Rscript'


def get_installed_version(module):
    cmnd = [RSCRIPT, '--slave', '--no-save', '--no-restore-history', '-e',
            'p <- installed.packages(); cat(p[p[,1] == "{name:}",'
            '3])'.format(name=module.params['name'])]
    (rc, stdout, stderr) = module.run_command(cmnd, check_rc=False)
    return stdout.strip() if rc == 0 else None


def install(module):
    cmnd = [RSCRIPT, '--slave', '--no-save', '--no-restore-history', '-e',
            'install.packages(pkgs="{name:}",repos="{repos:}")'
            ''.format(name=module.params['name'],
                      repos=module.params['repo'])]
    (rc, stdout, stderr) = module.run_command(cmnd, check_rc=True)
    return stderr


def uninstall(module):
    cmnd = [RSCRIPT, '--slave', '--no-save', '--no-restore-history', '-e',
            'remove.packages(pkgs="{name:}")'
            ''.format(name=module.params['name'])]
    (rc, stdout, stderr) = module.run_command(cmnd, check_rc=True)
    return stderr


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            name=dict(required=True),
            repo=dict(default='https://cran.rstudio.com/')
        )
    )
    state = module.params['state']
    name = module.params['name']
    changed = False
    version = get_installed_version(module)

    if state == 'present' and not version:
        stderr = install(module)
        version = get_installed_version(module)
        if not version:
            module.fail_json(
                msg='Failed to install {name:}: {err:}'.format(
                    name=name, err=stderr, version=version))
        changed = True

    elif state == 'absent' and version:
        stderr = uninstall(module)
        version = get_installed_version(module)
        if version:
            module.fail_json(
                msg='Failed to install {name:}: {err:}'.format(
                    name=name, err=stderr))
        changed = True

    module.exit_json(changed=changed, name=name, version=version)


if __name__ == '__main__':
    main()
