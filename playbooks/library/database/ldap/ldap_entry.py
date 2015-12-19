#!/usr/bin/env python

# ldap_entry Ansible module
# Copyright (C) 2014 Peter Sagerson <psagers@ignorare.net>
# Homepage: https://bitbucket.org/psagers/ansible-ldap


# Copyright (c) 2014, Peter Sagerson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from traceback import format_exc

import ldap
import ldap.modlist
import ldap.sasl


DOCUMENTATION = """
---
module: ldap_entry
short_description: Add or remove LDAP entries.
description:
    - Add or remove LDAP entries. This module only asserts the existence or
      non-existence of an LDAP entry, not its attributes. To assert the
      attribute values of an entry, see M(ldap_attr).
notes: []
version_added: null
author: Peter Sagerson
requirements:
    - python-ldap
options:
    dn:
        required: true
        description:
            - The DN of the entry to add or remove.
    state:
        required: false
        choices: [present, absent]
        default: present
        description:
            - The target state of the entry.
    objectClass:
        required: false
        description:
            - If C(state=present), this must be a list of objectClass values to
              use when creating the entry. It can either be a string containing
              a comma-separated list of values, or an actual list of strings.
    '...':
        required: false
        description:
            - If C(state=present), all additional arguments are taken to be
              LDAP attribute names like C(objectClass), with similar
              lists of values. These should only be used to
              provide the minimum attributes necessary for creating an entry;
              existing entries are never modified. To assert specific attribute
              values on an existing entry, see M(ldap_attr).
    server_uri:
        required: false
        default: ldapi:///
        description:
            - A URI to the LDAP server. The default value lets the underlying
              LDAP client library look for a UNIX domain socket in its default
              location.
    start_tls:
        required: false
        default: false
        description:
            - If true, we'll use the START_TLS LDAP extension.
    bind_dn:
        required: false
        description:
            - A DN to bind with. If this is omitted, we'll try a SASL bind with
              the EXTERNAL mechanism. If this is blank, we'll use an anonymous
              bind.
    bind_pw:
        required: false
        description:
            - The password to use with C(bind_dn).
"""


EXAMPLES = """
# Make sure we have a parent entry for users.
- ldap_entry: dn='ou=users,dc=example,dc=com' objectClass=organizationalUnit
  sudo: true

# Make sure we have an admin user.
- ldap_entry:
    dn: 'cn=admin,dc=example,dc=com'
    objectClass: simpleSecurityObject,organizationalRole
    description: An LDAP administrator
    userPassword: '{SSHA}pedsA5Y9wHbZ5R90pRdxTEZmn6qvPdzm'
  sudo: true

# Get rid of an old entry.
- ldap_entry: dn='ou=stuff,dc=example,dc=com' state=absent server_uri='ldap://localhost/' bind_dn='cn=admin,dc=example,dc=com' bind_pw=password
"""


def main():
    module = AnsibleModule(
        argument_spec={
            'dn': dict(required=True),
            'state': dict(default='present', choices=['present', 'absent']),
            'server_uri': dict(default='ldapi:///'),
            'start_tls': dict(default='false', choices=BOOLEANS),
            'bind_dn': dict(default=None),
            'bind_pw': dict(default=''),
        },
        check_invalid_arguments=False,
        supports_check_mode=True,
    )

    try:
        LdapEntry(module).main()
    except ldap.LDAPError, e:
        module.fail_json(msg=str(e), exc=format_exc())


class LdapEntry(object):
    _connection = None

    def __init__(self, module):
        self.module = module

        # python-ldap doesn't understand unicode strings. Parameters that are
        # just going to get passed to python-ldap APIs are stored as utf-8.
        self.dn = self._utf8_param('dn')
        self.state = self.module.params['state']
        self.server_uri = self.module.params['server_uri']
        self.start_tls = self.module.boolean(self.module.params['start_tls'])
        self.bind_dn = self._utf8_param('bind_dn')
        self.bind_pw = self._utf8_param('bind_pw')
        self.attrs = {}

        self._load_attrs()

        if (self.state == 'present') and ('objectClass' not in self.attrs):
            self.module.fail_json(msg="When state=present, at least one objectClass must be provided")

    def _utf8_param(self, name):
        return self._force_utf8(self.module.params[name])

    def _load_attrs(self):
        for name, raw in self.module.params.iteritems():
            if name not in self.module.argument_spec and not name.startswith('_') and name not in ['NO_LOG']:
                self.attrs[name] = self._load_attr_values(name, raw)

    def _load_attr_values(self, name, raw):
        if isinstance(raw, basestring):
            values = raw.split(',')
        else:
            values = raw

        if not (isinstance(values, list) and all(isinstance(value, basestring) for value in values)):
            self.module.fail_json(msg="{} must be a string or list of strings.".format(name))

        return map(self._force_utf8, values)

    def _force_utf8(self, value):
        """ If value is unicode, encode to utf-8. """
        if isinstance(value, unicode):
            value = value.encode('utf-8')

        return value

    def main(self):
        if self.state == 'present':
            action = self.handle_present()
        elif self.state == 'absent':
            action = self.handle_absent()
        else:
            action = None

        if (action is not None) and (not self.module.check_mode):
            action()

        self.module.exit_json(changed=(action is not None))

    #
    # State Implementations
    #

    def handle_present(self):
        """ If self.dn does not exist, returns a callable that will add it. """
        if not self.is_entry_present():
            modlist = ldap.modlist.addModlist(self.attrs)
            action = lambda: self.connection.add_s(self.dn, modlist)
        else:
            action = None

        return action

    def handle_absent(self):
        """ If self.dn exists, returns a callable that will delete it. """
        if self.is_entry_present():
            action = lambda: self.connection.delete_s(self.dn)
        else:
            action = None

        return action

    #
    # Util
    #

    def is_entry_present(self):
        try:
            self.connection.search_s(self.dn, ldap.SCOPE_BASE)
        except ldap.NO_SUCH_OBJECT:
            is_present = False
        else:
            is_present = True

        return is_present

    #
    # LDAP Connection
    #

    @property
    def connection(self):
        """ An authenticated connection to the LDAP server (cached). """
        if self._connection is None:
            self._connection = self._connect_to_ldap()

        return self._connection

    def _connect_to_ldap(self):
        connection = ldap.initialize(self.server_uri)

        if self.start_tls:
            connection.start_tls_s()

        if self.bind_dn is not None:
            connection.simple_bind_s(self.bind_dn, self.bind_pw)
        else:
            connection.sasl_interactive_bind_s('', ldap.sasl.external())

        return connection


from ansible.module_utils.basic import *  # noqa
main()
