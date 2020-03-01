# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2018 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import print_function
import os
import fnmatch
import re
from subprocess import check_output


# Fix "Edit on GitHub" links in the documentation
# Jinja2 Support is only basic Jinja2 without all the good stuff from Ansible.
# So I am not gonna mess with that or try to extend it as in:
# https://stackoverflow.com/questions/36019670/
# What I am gonna do instead is just recompute source file to URL map in Python
# and job done.

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def get_source_file_to_url_map(start_dir='.', skip_patterns=[]):
    source_file_to_url_map = {}
    repo_dir_to_url_map = {}

    cur_dir = os.path.abspath(start_dir)

    for source_file_name in find_files('.', '*.rst'):
        pagename_source_file = source_file_name.lstrip('/.')

        skip = False
        for skip_pattern in skip_patterns:
            if re.search(skip_pattern, pagename_source_file):
                skip = True
                break

        if skip:
            continue

        dir_path = os.path.dirname(source_file_name)
        if len(dir_path) > 2:
            dir_path = dir_path.lstrip('/.')

        # Can also contain subdirs in a repo but this optimization should
        # already get factor 10 in performance for git invocation.
        if dir_path not in repo_dir_to_url_map:
            for remote_line in check_output(['git', '-C', dir_path,
                                             'remote', '-v']).split(b'\n'):
                remote_item = re.split(r'\s', remote_line.decode('utf-8'))
                if remote_item[0] == 'origin' and remote_item[2] == '(fetch)':
                    base_url = remote_item[1]

                    if base_url.endswith('.git'):
                        base_url = base_url[:-4]

                    if '@' in base_url:  # it's a git+ssh URL
                        base_url = base_url.replace(':', '/')
                        base_url = base_url.replace('git@', 'https://')
                    repo_dir_to_url_map[dir_path] = base_url

        relative_pagename = 'docs/' + pagename_source_file

        if re.match(r'docs/news/changelog(?:\.rst)$',
                    relative_pagename, flags=re.I):
            relative_pagename = 'CHANGELOG.rst'

        if re.match(r'docs/user-guide/install(?:\.rst)$',
                    relative_pagename, flags=re.I):
            relative_pagename = 'INSTALL.rst'

        relative_path = re.match(
                r'docs/ansible/roles/(.*)/defaults/(.+)\.rst$',
                relative_pagename, flags=re.I)
        if relative_path:
            relative_pagename = ('ansible/roles/' + relative_path.group(1)
                                 + '/defaults/' + relative_path.group(2)
                                 + '.yml')

        pagename_source_file = re.sub(r'\.rst$', '', pagename_source_file)
        source_file_to_url_map[pagename_source_file] = {
            'url': repo_dir_to_url_map[dir_path],
            'pagename': relative_pagename,
        }

    return source_file_to_url_map
