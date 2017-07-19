# Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
# Copyright (C) 2017 DebOps https://debops.org/

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

__metaclass__ = type


def _parse_kv_value(current_data, new_data, data_index, *args, **kwargs):
    """Parse the parameter values and merge
    with existing ones conditionally.
    """

    if 'value' in new_data:
        old_value = current_data.get('value', None)
        old_state = current_data.get('state', 'present')
        new_value = new_data.get('value')

        if isinstance(new_value, (str, unicode, int, float, bool)):
            if (old_value is None or isinstance(old_value,
                                                (str, unicode, int,
                                                 float, bool, dict))):
                current_data.update({'value': new_value})

            if (old_value is not None and old_state in ['comment']):
                current_data.update({'state': 'present'})

        elif isinstance(new_value, list):
            if (old_value is None or isinstance(old_value, dict)):
                dict_value = current_data.get('value', {}).copy()

            elif isinstance(old_value, (str, unicode, int, float, bool)):
                dict_value = {}

            for element_index, element in enumerate(new_value):
                if isinstance(element, (str, unicode, int)):
                    dict_element = dict_value.get(element, {}).copy()
                    if not dict_element.get('name'):
                        dict_element.update({
                            'name': element,
                            'id': ((data_index * 10) + element_index),
                            'weight': dict_element.get('weight', 0),
                            'state': 'present'})

                        dict_element['real_weight'] = (
                            int(dict_element.get('id'))
                            + int(dict_element.get('weight')))

                        dict_value.update({element: dict_element})
                        current_data.update({'value': dict_value})

                elif (isinstance(element, dict) and
                        element.get('param', element.get('name')) and
                        element.get('state', 'present') != 'ignore'):
                    element_name = element.get('param', element.get('name'))
                    dict_element = dict_value.get(element_name, {}).copy()
                    dict_element.update({
                        'name': element_name,
                        'id': ((data_index * 10) + element_index),
                        'weight': int(dict_element.get('weight', 0)),
                        'state': element.get('state', 'present')
                    })

                    if 'weight' in element:
                        dict_element['weight'] = (
                            int(element.get('weight',
                                dict_element.get('weight', 0)))
                            + int(dict_element.get('weight', 0)))

                    dict_element['real_weight'] = (
                        int(dict_element.get('id'))
                        + int(dict_element.get('weight')))

                    dict_value.update({element_name: dict_element})
                    current_data.update({'value': dict_value})


def parse_kv_config(*args, **kwargs):
    """Return a parsed list of key/value configuration options"""

    input_args = []
    parsed_config = {}

    # Flatten the input list
    for sublist in list(args):
        for item in sublist:
            input_args.append(item)

    for element_index, element in enumerate(input_args):
        if isinstance(element, dict):
            if (any(x in ['name'] for x in element) and
                    element.get('state', 'present') != 'ignore'):

                param_name = element.get('name')

                if element.get('state', 'present') == 'append':

                    # In append mode, don't create new config entries
                    if param_name not in parsed_config.keys():
                        continue

                current_param = (parsed_config[param_name].copy()
                                 if param_name in parsed_config
                                 else {})

                if element.get('state', 'present') != 'append':
                    current_param['state'] = (element.get('state',
                                              current_param.get('state',
                                                                'present')))
                elif element.get('state', 'present') == 'append':
                    current_param['state'] = current_param.get('state',
                                                               'present')

                current_param.update({
                    'name': param_name,  # in case of a new entry
                    'id': int(current_param.get('id', (element_index * 10))),
                    'weight': int(current_param.get('weight', 0)),
                    'separator': element.get('separator',
                                             current_param.get('separator',
                                                               False)),
                    'section': element.get('section',
                                           current_param.get('section',
                                                             'unknown'))
                })

                if 'weight' in element:
                    current_param['weight'] = (
                        int(element.get('weight',
                            current_param.get('weight', 0)))
                        + int(current_param.get('weight', 0)))

                current_param['real_weight'] = (
                    int(current_param.get('id'))
                    + int(current_param.get('weight')))

                _parse_kv_value(current_param, element, element_index)

                if 'option' in element:
                    current_param['option'] = element.get('option')

                if 'comment' in element:
                    current_param['comment'] = element.get('comment')

                parsed_config.update({param_name: current_param})

            # These parameters are special and should not be interpreted
            # directly as configuration options
            elif not all(x in ['name', 'option', 'state', 'comment',
                               'section', 'weight', 'value']
                         for x in element):
                for key, value in element.iteritems():
                    current_param = (parsed_config[key].copy()
                                     if key in parsed_config else {})
                    current_param.update({
                        'name': key,
                        'state': 'present',
                        'id': int(current_param.get('id',
                                                    (element_index * 10))),
                        'weight': int(current_param.get('weight', 0)),
                        'section': current_param.get('section', 'unknown')
                    })

                    current_param['real_weight'] = (
                        int(current_param.get('id'))
                        + int(current_param.get('weight')))

                    _parse_kv_value(current_param,
                                    {'value': value},
                                    element_index)

                    parsed_config.update({key: current_param})

    # Expand the dictionary of configuration options into a list,
    # and return sorted by weight
    output = []
    for key, params in parsed_config.iteritems():
        if isinstance(params.get('value'), dict):
            unsorted_values = []
            current_value = params.get('value').copy()

            for param_value in current_value.values():
                unsorted_values.append(param_value)
                params.update({'value': sorted(unsorted_values,
                                               key=itemgetter('real_weight'))})

            output.append(params)
        else:
            output.append(params)

    return sorted(output, key=itemgetter('real_weight'))


def postfix__parse_mastercf(*args, **kwargs):
    """Return a parsed list of Postfix master.cf options"""

    input_args = []
    parsed_config = {}

    # Flatten the input list
    for sublist in list(args):
        for item in sublist:
            input_args.append(item)

    for element_index, element in enumerate(input_args):
        if isinstance(element, dict):
            if (any(x in ['name'] for x in element) and
                    element.get('state', 'present') != 'ignore'):

                param_name = element.get('name')

                if element.get('state', 'present') == 'append':

                    # In append mode, don't create new config entries
                    if param_name not in parsed_config.keys():
                        continue

                current_param = (parsed_config[param_name].copy()
                                 if param_name in parsed_config
                                 else {})

                if element.get('state', 'present') != 'append':
                    current_param['state'] = (element.get('state',
                                              current_param.get('state',
                                                                'present')))
                elif element.get('state', 'present') == 'append':
                    current_param['state'] = current_param.get('state',
                                                               'present')

                current_param.update({
                    'name': param_name,  # in case of a new entry
                    'id': int(current_param.get('id', (element_index * 10))),
                    'weight': int(current_param.get('weight', 0)),
                    'separator': element.get('separator',
                                             current_param.get('separator',
                                                               False)),
                    'type': element.get('type',
                                        current_param.get('type')),
                    'private': element.get('private',
                                           current_param.get('private',
                                                             '-')),
                    'unpriv': element.get('unpriv',
                                          current_param.get('unpriv',
                                                            '-')),
                    'chroot': element.get('chroot',
                                          current_param.get('chroot',
                                                            '-')),
                    'wakeup': element.get('wakeup',
                                          current_param.get('wakeup',
                                                            '-')),
                    'maxproc': element.get('maxproc',
                                           current_param.get('maxproc',
                                                             '-')),
                    'command': element.get('command',
                                           current_param.get('command'))
                })

                if 'weight' in element:
                    current_param['weight'] = (
                        int(element.get('weight',
                            current_param.get('weight', 0)))
                        + int(current_param.get('weight', 0)))

                current_param['real_weight'] = (
                    int(current_param.get('id'))
                    + int(current_param.get('weight')))

                if current_param['command'] is None:
                    current_param['command'] = (
                        current_param.get('service',
                                          current_param.get('name')))

                if 'service' in element:
                    current_param['service'] = element.get('service')

                if 'args' in element:
                    current_param['args'] = element.get('args')

                if 'comment' in element:
                    current_param['comment'] = element.get('comment')

                if 'options' in element:
                    current_options = current_param.get('options', [])
                    new_options = parse_kv_config(
                        current_options + element.get('options'))

                    current_param['options'] = new_options

                parsed_config.update({param_name: current_param})

    # Expand the dictionary of configuration options into a list,
    # and return sorted by weight
    output = []
    for key, params in parsed_config.iteritems():
        if isinstance(params.get('value'), dict):
            unsorted_values = []
            current_value = params.get('value').copy()

            for param_value in current_value.values():
                unsorted_values.append(param_value)
                params.update({'value': sorted(unsorted_values,
                                               key=itemgetter('real_weight'))})

            output.append(params)
        else:
            output.append(params)

    return sorted(output, key=itemgetter('real_weight'))


class FilterModule(object):
    """Register custom filter plugins in Ansible"""

    def filters(self):
        return {
            'parse_kv_config': parse_kv_config,
            'postfix__parse_mastercf': postfix__parse_mastercf
        }
