# Copyright (C) 2017, Matt Martz <matt@sivel.net>
# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
from collections.abc import Mapping

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_text

try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False


def _check_toml(func):
    @functools.wraps(func)
    def inner(o):
        if not HAS_TOML:
            raise AnsibleFilterError(
                f'The {func.__name__} filter plugin requires '
                f'the python "toml" library')
        return func(o)
    return inner


def _to_native(obj):
    """Convert Ansible-specific objects to native Python types.

    Ansible values can be instances of custom 'str', 'int' or 'list'
    subclasses, for example the tagged objects used by ansible-core v2.19
    and newer. The 'toml' library selects a serializer by an exact 'type()'
    match and would otherwise serialize such values incorrectly, for example
    as an array of characters instead of a string.
    """
    if isinstance(obj, dict):
        return {_to_native(k): _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(v) for v in obj]
    if isinstance(obj, bool) or obj is None:
        return obj
    if isinstance(obj, str):
        return str(obj)
    if isinstance(obj, int):
        return int(obj)
    if isinstance(obj, float):
        return float(obj)
    return obj


@_check_toml
def from_toml(o):
    if not isinstance(o, str):
        raise AnsibleFilterError(f'from_toml requires a string, got {type(o)}')
    return toml.loads(to_text(o, errors='surrogate_or_strict'))


@_check_toml
def to_toml(o):
    if not isinstance(o, Mapping):
        raise AnsibleFilterError(f'to_toml requires a dict, got {type(o)}')
    return to_text(toml.dumps(_to_native(o)), errors='surrogate_or_strict')


class FilterModule:
    def filters(self):
        return {
            'to_toml': to_toml,
            'from_toml': from_toml,
        }
