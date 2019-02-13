# Copyright (C) 2015 Maciej Delmanowski <drybjed@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <https://www.gnu.org/licenses/>.

from ansible import errors

try:
    import fnmatch
except Exception as e:
    raise errors.AnsibleFilterError('fnmatch python library not found')


def globmatch_filter(value, pattern):
    ''' Return string or list of items matching given glob pattern(s). '''

    if not isinstance(pattern, (list, tuple)):
        pattern = [pattern]

    if isinstance(value, (list, tuple)):
        _ret = []

        for element in pattern:
            for entry in value:
                if fnmatch.fnmatch(str(entry), str(element)):
                    if entry not in _ret:
                        _ret.append(entry)

        if _ret:
            return _ret
        else:
            return list()

    else:

        for element in pattern:
            if fnmatch.fnmatch(str(value), str(element)):
                return value


class FilterModule(object):

    ''' Return string or list of items matching given glob pattern(s). '''
    def filters(self):
        return {
            'globmatch': globmatch_filter
        }
