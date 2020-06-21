# Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017 DebOps <https://debops.org/>
# SPDX-License-Identifier: GPL-3.0-or-later

# This file is part of DebOps.
#
# DebOps is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DebOps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DebOps. If not, see <https://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
from operator import itemgetter

try:
    unicode = unicode
except NameError:
    # py3
    unicode = str

__metaclass__ = type


def _mangle_recipients(name, *args):
    """Modify the recipient address if it's the same as alias
    to prevent mail forwarding loops
    Ref: https://serverfault.com/questions/471604/
    """

    input_args = []

    # Flatten the input list
    for sublist in list(args):
        for item in sublist:
            input_args.append(item)

    if name in input_args:
        return [w.replace(name, '\\' + name) for w in input_args]
    else:
        return input_args


def _update_recipients(current_data, new_data, *args, **kwargs):
    """Replace the current list of recipients with a new one"""

    for selector in args:
        if selector in new_data:
            new_recipients = ([new_data.get(selector)]
                              if isinstance(new_data.get(selector),
                                            (str, unicode))
                              else new_data.get(selector))
            current_data.update({'recipients':
                                _mangle_recipients(current_data.get('name'),
                                                   new_recipients)})


def _add_recipients(current_data, new_data, *args, **kwargs):
    """Add mail recipients to an existing list of recipients"""

    for selector in args:
        if selector in new_data:
            current_recipients = current_data.get('recipients', [])
            current_recipients.extend([new_data.get(selector)]
                                      if isinstance(new_data.get(selector),
                                                    (str, unicode))
                                      else new_data.get(selector))
            current_data.update({'recipients':
                                _mangle_recipients(current_data.get('name'),
                                                   current_recipients)})


def _del_recipients(current_data, new_data, *args, **kwargs):
    """Remove mail recipients from an existing list"""

    for selector in args:
        if selector in new_data:
            deleted_recipients = ([new_data.get(selector)]
                                  if isinstance(new_data.get(selector),
                                                (str, unicode))
                                  else new_data.get(selector))
            current_recipients = current_data.get('recipients', [])
            new_recipients = [x for x in current_recipients
                              if x not in deleted_recipients]
            current_data.update({'recipients': new_recipients})


def etc_aliases_parse_recipients(*args, **kwargs):
    """Return a parsed list of mail aliases and recipients"""

    input_args = []
    parsed_aliases = {}

    # Flatten the input list
    for sublist in list(args):
        for item in sublist:
            input_args.append(item)

    for element in input_args:
        if isinstance(element, dict):
            if (any(x in element for x in ['name', 'alias']) and
                    element.get('state', 'present') != 'ignore'):

                alias_name = element.get('alias', element.get('name'))
                current_alias = (parsed_aliases[alias_name].copy()
                                 if alias_name in parsed_aliases
                                 else {})

                current_alias.update({
                    'name': alias_name,  # in case of a new entry
                    'state': element.get('state',
                                         current_alias.get('state',
                                                           'present')),
                    'weight': int(element.get('weight',
                                  current_alias.get('weight', 0))),
                    'section': element.get('section',
                                           current_alias.get('section',
                                                             'unknown'))
                })

                _update_recipients(current_alias, element, 'dest', 'to')

                _add_recipients(current_alias, element,
                                'add_dest', 'add_to', 'cc', 'bcc')

                _del_recipients(current_alias, element,
                                'del_dest', 'del_to')

                if 'real_name' in element or 'real_alias' in element:
                    current_alias['real_name'] = (
                        element.get('real_name',
                                    element.get('real_alias')))

                if 'comment' in element:
                    current_alias['comment'] = element.get('comment')

                if not current_alias.get('recipients', ''):
                    current_alias['state'] = 'comment'

                parsed_aliases.update({alias_name: current_alias})

            # These parameters are special and should not be interpreted
            # directly as mail aliases.
            elif not all(x in ['name', 'alias', 'state', 'comment',
                               'section', 'weight', 'dest', 'to',
                               'add_dest', 'add_to', 'cc', 'bcc',
                               'del_dest', 'del_to']
                         for x in element):
                for key, value in element.items():
                    current_alias = parsed_aliases.get(key, {}).copy()
                    current_alias.update({
                        'name': key,
                        'recipients': (_mangle_recipients(
                                       current_alias.get('name'), [value]
                                       if isinstance(value, (str, unicode))
                                       else value)),
                        'state': 'present',
                        'weight': int(element.get('weight',
                                      current_alias.get('weight', 0))),
                        'section': current_alias.get('section', 'unknown')
                    })

                    current_alias.update({
                        'recipients': (_mangle_recipients(
                                       current_alias.get('name'),
                                       ([value]
                                        if isinstance(value, (str, unicode))
                                        else value)))
                    })

                    if not current_alias.get('recipients', ''):
                        current_alias['state'] = 'comment'

                    parsed_aliases[key] = current_alias

    # Expand the dictionary of aliases into a list,
    # and return sorted by weight.
    return sorted(parsed_aliases.values(), key=itemgetter('weight', 'name'))


class FilterModule(object):
    """Register custom filter plugins in Ansible"""

    def filters(self):
        return {'etc_aliases_parse_recipients': etc_aliases_parse_recipients}
