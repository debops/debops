# Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2026 DebOps <https://debops.org/>
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

"""Build the ferm dependent rules that firewall published Docker ports."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
from collections import Counter

from ansible.errors import AnsibleFilterError

__all__ = ('docker_service_ferm_rules',)

REJECT_WITH = {
    'tcp': 'tcp-reset',
    'udp': 'icmp-port-unreachable',
}

DEFAULT_REJECT_WITH = 'icmp-admin-prohibited'

UNSAFE_NAME_CHARS = re.compile(r'[^A-Za-z0-9._-]')


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _interface_key(interface):
    if isinstance(interface, str):
        return interface
    if interface:
        return '-'.join(str(entry) for entry in interface)
    return ''


def _reject_with(protocol):
    return REJECT_WITH.get(protocol, DEFAULT_REJECT_WITH)


def _rule_name(service_name, port, protocol, default_chain, chain, dport,
               interface_key):
    """Compose a ferm rule name.

    The ferm dependent rule list is keyed by name, so every field that can
    differ between two entries sharing a host port has to end up in the name
    or later entries silently overwrite earlier ones.
    """
    name_bits = ['docker_service', service_name, port, protocol]
    if chain != default_chain:
        name_bits.append(chain)
    if dport != port:
        name_bits.append('dst' + dport)
    if interface_key:
        name_bits.append(UNSAFE_NAME_CHARS.sub('_', interface_key))
    return '_'.join(name_bits)


def _published_port_rules(service, defaults):
    service_name = str(service['name'])
    service_state = service.get('state', 'present')
    if service_state in ('absent', 'ignore'):
        return []

    rules = []
    for port_entry in _as_list(service.get('published_ports')):
        allow = _as_list(port_entry.get('allow'))
        if not allow:
            continue

        port = str(port_entry.get('port'))
        protocol = str(port_entry.get('protocol', defaults['protocol']))
        default_chain = str(defaults['chain'])
        chain = str(port_entry.get('chain', default_chain))
        action = port_entry.get('action_default', defaults['action'])
        target = 'REJECT' if action == 'reject' else 'DROP'

        # After Docker DNAT, filter chains other than INPUT see the container
        # destination port. INPUT (host network) still matches the host-side
        # port.
        if chain == 'INPUT':
            dport = port
        else:
            dport = str(port_entry.get('container_port', port_entry.get('port')))

        interface = port_entry.get(
            'interface', port_entry.get('interfaces'))
        interface_key = _interface_key(interface)

        name = _rule_name(service_name, port, protocol, default_chain, chain,
                          dport, interface_key)
        comment = port_entry.get(
            'comment',
            '{0} port {1}/{2} (DOCKER-USER)'.format(
                service_name, port, protocol))

        rule = {
            'name': name,
            'by_role': 'debops.docker_service',
            'comment': comment,
            'rules': [
                {
                    'chain': chain,
                    'type': 'accept',
                    'protocol': protocol,
                    'dport': [dport],
                    'saddr': allow,
                },
                {
                    'chain': chain,
                    'type': 'accept',
                    'target': target,
                    'accept_any': True,
                    'protocol': protocol,
                    'dport': [dport],
                    'reject_with': _reject_with(protocol),
                },
            ],
        }

        if interface:
            for rule_body in rule['rules']:
                rule_body['interface'] = interface

        rules.append(rule)

    return rules


def _stale_rules(rule_names, on_disk):
    return [
        {
            'name': name,
            'state': 'absent',
            'by_role': 'debops.docker_service',
        }
        for name in on_disk
        if name not in rule_names
    ]


def docker_service_ferm_rules(services, default_chain='DOCKER-USER',
                              default_protocol='tcp', default_action='reject',
                              on_disk_rule_names=None):
    """Return the ferm dependent rules for the published ports of ``services``.

    ``on_disk_rule_names`` lists the rule names still present on the managed
    host, so that rules dropped from the configuration are removed instead of
    being left in place.
    """
    defaults = {
        'chain': default_chain,
        'protocol': default_protocol,
        'action': default_action,
    }

    rules = []
    for service in _as_list(services):
        rules.extend(_published_port_rules(service, defaults))

    names = [rule['name'] for rule in rules]
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        raise AnsibleFilterError(
            "The docker_service role generated duplicate ferm rule names: "
            "{0}. Two published_ports entries which differ only in a value "
            "not part of the rule name collide.".format(', '.join(duplicates))
        )

    rules.extend(_stale_rules(set(names), _as_list(on_disk_rule_names)))
    return rules


class FilterModule(object):
    """Register custom filter plugins in Ansible"""

    def filters(self):
        return {'docker_service_ferm_rules': docker_service_ferm_rules}
