#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2016, Peter Sagerson <psagers@ignorare.net>
# (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
# (c) 2017, Alexander Korinek <noles@a3k.net>
#
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native, to_bytes

import traceback
import re

try:
    import ldap
    import ldap.sasl

    HAS_LDAP = True
except ImportError:
    HAS_LDAP = False

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = """
---
module: ldap_attrs
short_description: Add or remove multiple LDAP attribute values.
description:
  - Add or remove multiple LDAP attribute values.
notes:
  - This only deals with attributes on existing entries. To add or remove
    whole entries, see M(ldap_entry).
  - The default authentication settings will attempt to use a SASL EXTERNAL
    bind over a UNIX domain socket. This works well with the default Ubuntu
    install for example, which includes a cn=peercred,cn=external,cn=auth ACL
    rule allowing root to modify the server configuration. If you need to use
    a simple bind to access your server, pass the credentials in I(bind_dn)
    and I(bind_pw).
  - For I(state=present) and I(state=absent), all value comparisons are
    performed on the server for maximum accuracy. For I(state=exact), values
    have to be compared in Python, which obviously ignores LDAP matching
    rules. This should work out in most cases, but it is theoretically
    possible to see spurious changes when target and actual values are
    semantically identical but lexically distinct.
version_added: '2.5'
author:
  - Jiri Tyr (@jtyr)
  - Alexander Korinek (@noles)
requirements:
  - python-ldap
options:
  bind_dn:
    required: false
    default: null
    description:
      - A DN to bind with. If this is omitted, we'll try a SASL bind with
        the EXTERNAL mechanism. If this is blank, we'll use an anonymous
        bind.
  bind_pw:
    required: false
    default: null
    description:
      - The password to use with I(bind_dn).
  dn:
    required: true
    description:
      - The DN of the entry to modify.
  server_uri:
    required: false
    default: ldapi:///
    description:
      - A URI to the LDAP server. The default value lets the underlying
        LDAP client library look for a UNIX domain socket in its default
        location.
  start_tls:
    required: false
    choices: ['yes', 'no']
    default: 'no'
    description:
      - If true, we'll use the START_TLS LDAP extension.
  state:
    required: false
    choices: [present, absent, exact]
    default: present
    description:
      - The state of the attribute values. If C(present), all given
        values will be added if they're missing. If C(absent), all given
        values will be removed if present. If C(exact), the set of values
        will be forced to exactly those provided and no others. If
        I(state=exact) and I(value) is empty, all values for this
        attribute will be removed.
  attributes:
    required: true
    description:
      - The attribute(s) and value(s) to add or remove. The complex argument
        format is required in order to pass a list of strings (see examples).
  ordered:
    required: false
    choices: ['yes', 'no']
    default: 'no'
    description:
      - If C(yes), prepend list values with X-ORDERED index numbers in all
        attributes specified in the current task. This is useful mostly with
        I(olcAccess) attribute to easily manage LDAP Access Control Lists.
  validate_certs:
    required: false
    choices: ['yes', 'no']
    default: 'yes'
    description:
      - If C(no), SSL certificates will not be validated. This should only be
        used on sites using self-signed certificates.
"""


EXAMPLES = """
- name: Configure directory number 1 for example.com
  ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
        olcSuffix: dc=example,dc=com
    state: exact

# The complex argument format is required here to pass a list of ACL strings.
- name: Set up the ACL
  ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
        olcAccess:
          - >-
            {0}to attrs=userPassword,shadowLastChange
            by self write
            by anonymous auth
            by dn="cn=admin,dc=example,dc=com" write
            by * none'
          - >-
            {1}to dn.base="dc=example,dc=com"
            by dn="cn=admin,dc=example,dc=com" write
            by * read
    state: exact

# An alternative approach with automatic X-ORDERED numbering
- name: Set up the ACL
  ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
        olcAccess:
          - >-
            to attrs=userPassword,shadowLastChange
            by self write
            by anonymous auth
            by dn="cn=admin,dc=example,dc=com" write
            by * none'
          - >-
            to dn.base="dc=example,dc=com"
            by dn="cn=admin,dc=example,dc=com" write
            by * read
    ordered: yes
    state: exact

- name: Declare some indexes
  ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
        olcDbIndex:
            - objectClass eq
            - uid eq

- name: Set up a root user, which we can use later to bootstrap the directory
  ldap_attrs:
    dn: olcDatabase={1}hdb,cn=config
    attributes:
        olcRootDN: cn=root,dc=example,dc=com
        olcRootPW: "{SSHA}tabyipcHzhwESzRaGA7oQ/SDoBZQOGND"
    state: exact

- name: Get rid of an unneeded attribute
  ldap_attrs:
    dn: uid=jdoe,ou=people,dc=example,dc=com
    attributes:
        shadowExpire: ""
    state: exact
    server_uri: ldap://localhost/
    bind_dn: cn=admin,dc=example,dc=com
    bind_pw: password

#
# The same as in the previous example but with the authentication details
# stored in the ldap_auth variable:
#
# ldap_auth:
#   server_uri: ldap://localhost/
#   bind_dn: cn=admin,dc=example,dc=com
#   bind_pw: password
- name: Get rid of an unneeded attribute
  ldap_attrs:
    dn: uid=jdoe,ou=people,dc=example,dc=com
    attributes:
        shadowExpire: ""
    state: exact
    params: "{{ ldap_auth }}"
"""


RETURN = """
modlist:
  description: list of modified parameters
  returned: success
  type: list
  sample: '[[2, "olcRootDN", ["cn=root,dc=example,dc=com"]]]'
"""


class LdapAttr(object):
    def __init__(self, module):
        # Shortcuts
        self.module = module
        self.bind_dn = self.module.params['bind_dn']
        self.bind_pw = self.module.params['bind_pw']
        self.dn = self.module.params['dn']
        self.server_uri = self.module.params['server_uri']
        self.start_tls = self.module.params['start_tls']
        self.state = self.module.params['state']
        self.verify_cert = self.module.params['validate_certs']
        self.attrs = self.module.params['attributes']
        self.ordered = self.module.params['ordered']

        # Establish connection
        self.connection = self._connect_to_ldap()

    def _order_values(self, values):
        """ Preprend X-ORDERED index numbers to attribute's values. """
        ordered_values = []

        if isinstance(values, list):
            for index, value in enumerate(values):
                cleaned_value = re.sub(r'^\{\d+\}', '', value)
                ordered_values.append('{' + str(index) + '}' + cleaned_value)

        return ordered_values

    def _normalize_values(self, values):
        """ Normalize attribute's values. """
        norm_values = []

        if isinstance(values, list):
            if self.ordered:
                norm_values = list(map(to_bytes,
                                   self._order_values(list(map(str,
                                                               values)))))
            else:
                norm_values = list(map(to_bytes, values))
        elif values != "":
            norm_values = [to_bytes(str(values))]

        return norm_values

    def add(self):
        modlist = []
        for name, values in self.module.params['attributes'].items():
            norm_values = self._normalize_values(values)
            for value in norm_values:
                if self._is_value_absent(name, value):
                    modlist.append((ldap.MOD_ADD, name, value))

        return modlist

    def delete(self):
        modlist = []
        for name, values in self.module.params['attributes'].items():
            norm_values = self._normalize_values(values)
            for value in norm_values:
                if self._is_value_present(name, value):
                    modlist.append((ldap.MOD_DELETE, name, value))

        return modlist

    def exact(self):
        modlist = []
        for name, values in self.module.params['attributes'].items():
            norm_values = self._normalize_values(values)
            try:
                results = self.connection.search_s(
                    self.dn, ldap.SCOPE_BASE, attrlist=[name])
            except ldap.LDAPError as e:
                self.module.fail_json(
                    msg="Cannot search for attribute %s" % name,
                    details=to_native(e))

            current = results[0][1].get(name, [])

            if frozenset(norm_values) != frozenset(current):
                if len(current) == 0:
                    modlist.append((ldap.MOD_ADD, name, norm_values))
                elif len(norm_values) == 0:
                    modlist.append((ldap.MOD_DELETE, name, None))
                else:
                    modlist.append((ldap.MOD_REPLACE, name, norm_values))

        return modlist

    def _is_value_present(self, name, value):
        """ True if the target attribute has the given value. """
        try:
            is_present = bool(
                self.connection.compare_s(self.dn, name, value))
        except ldap.NO_SUCH_ATTRIBUTE:
            is_present = False

        return is_present

    def _is_value_absent(self, name, value):
        """ True if the target attribute doesn't have the given value. """
        return not self._is_value_present(name, value)

    def _connect_to_ldap(self):
        if not self.verify_cert:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        connection = ldap.initialize(self.server_uri)

        if self.start_tls:
            try:
                connection.start_tls_s()
            except ldap.LDAPError as e:
                self.module.fail_json(msg="Cannot start TLS.",
                                      details=to_native(e))

        try:
            if self.bind_dn is not None:
                connection.simple_bind_s(self.bind_dn, self.bind_pw)
            else:
                connection.sasl_interactive_bind_s('', ldap.sasl.external())
        except ldap.LDAPError as e:
            self.module.fail_json(
                msg="Cannot bind to the server.", details=to_native(e))

        return connection


def main():
    module = AnsibleModule(
        argument_spec={
            'bind_dn': dict(default=None),
            'bind_pw': dict(default='', no_log=True),
            'dn': dict(required=True),
            'params': dict(type='dict'),
            'server_uri': dict(default='ldapi:///'),
            'start_tls': dict(default=False, type='bool'),
            'state': dict(
                default='present',
                choices=['present', 'absent', 'exact']),
            'attributes': dict(required=True, type='dict'),
            'ordered': dict(default=False, type='bool'),
            'validate_certs': dict(default=True, type='bool'),
        },
        supports_check_mode=True,
    )

    if not HAS_LDAP:
        module.fail_json(
            msg="Missing required 'ldap' module (pip install python-ldap)")

    # Update module parameters with user's parameters if defined
    if 'params' in module.params and isinstance(module.params['params'], dict):
        module.params.update(module.params['params'])
        # Remove the params
        module.params.pop('params', None)

    # Instantiate the LdapAttr object
    ldap = LdapAttr(module)

    state = module.params['state']

    # Perform action
    if state == 'present':
        modlist = ldap.add()
    elif state == 'absent':
        modlist = ldap.delete()
    elif state == 'exact':
        modlist = ldap.exact()

    changed = False

    if len(modlist) > 0:
        changed = True

        if not module.check_mode:
            try:
                ldap.connection.modify_s(ldap.dn, modlist)
            except Exception as e:
                module.fail_json(msg="Attribute action failed.",
                                 details=to_native(e),
                                 exception=traceback.format_exc())

    module.exit_json(changed=changed, modlist=modlist)


if __name__ == '__main__':
    main()
