# coding: utf-8

# Copyright (C) 2015 Patryk Ściborek <patryk@sciborek.com>
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

from __future__ import absolute_import

import os
import hashlib
import base64

from ansible import errors


def ldappassword(secret, schema='SHA', salt=None):
    '''Return password hash to be used as userPassword value'''
    hash_types = {
        'SHA': 'sha1',
        'SSHA': 'sha1',
        'MD5': 'md5',
        'SMD5': 'md5',
    }

    try:
        htype = hash_types[schema]
    except KeyError:
        raise errors.AnsibleFilterError(
            'Unknown/unsupported storage schema: {}'.format(schema))

    h = hashlib.new(htype)
    h.update(secret.encode())

    if schema in ('SSHA', 'SMD5'):
        if salt is None:
            salt = base64.standard_b64encode(os.urandom(4))
        h.update(salt)
    else:
        salt = ''.encode()

    rv = base64.standard_b64encode(h.digest()+salt)
    return '{{{}}}{}'.format(schema, rv.decode())


class FilterModule(object):
    def filters(self):
        return {
            'ldappassword': ldappassword,
        }
