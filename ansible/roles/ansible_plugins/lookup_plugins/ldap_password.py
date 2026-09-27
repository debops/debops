# -*- coding: utf-8 -*-
# Copyright (C) 2022 David Härdeman <david@hardeman.nu>
# Copyright (C) 2022 DebOps <https://debops.org/>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import uuid

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.plugins.loader import lookup_loader
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.utils.display import Display

display = Display()

# This UUID is from the Ansible to_uuid filter, we need to use the same seed
# in order to ensure idempotency and a one-to-one mapping between our custom
# plugin and Ansible's filter.
UUID_NAMESPACE_ANSIBLE = uuid.UUID('361E6D51-FAEC-444A-9079-341386DA8E2E')


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        ret = []

        if len(terms) != 3:
            raise AnsibleError('ldap_password: three arguments expected')

        bdir = self._loader.path_dwim(terms[0].rstrip('/'))
        dn = terms[1]
        params = terms[2]
        dn_uuid = to_text(uuid.uuid5(UUID_NAMESPACE_ANSIBLE,
                          to_native(dn, errors='surrogate_or_strict')))
        pw_path = '{bdir}/{uuid}.password'.format(bdir=bdir, uuid=dn_uuid)
        log_path = '{bdir}/debops_ldap_uuid.log'.format(bdir=bdir)
        pw_terms = [pw_path + ((' ' + params) if len(params) > 0 else '')]

        pw_lookup = lookup_loader.get('ansible.builtin.password',
                                      loader=self._loader,
                                      templar=self._templar)

        pw = pw_lookup.run(pw_terms, variables=None, validate_certs=True)

        with open(log_path, 'a+') as log_file:
            log_file.seek(0)
            found = False

            for raw_line in log_file:
                line = raw_line.strip()
                if len(line) == 0 or line.startswith('#'):
                    continue

                parts = line.split(' ', 1)
                if len(parts) != 2:
                    continue

                log_uuid = parts[0].strip()
                log_dn = parts[1].strip()

                if len(log_dn) == 0 or len(log_uuid) == 0:
                    continue

                if log_uuid != dn_uuid:
                    continue

                if log_dn != dn:
                    raise AnsibleError('ldap_password: DN <-> UUID mismatch')

                found = True
                display.vvvv('ldap_password: existing entry - ' +
                             'UUID: {uuid}, DN: {dn}\n'.format(uuid=dn_uuid, dn=dn))
                break

            if not found:
                log_file.write('{uuid} {dn}\n'.format(uuid=dn_uuid, dn=dn))
                display.vvvv('ldap_password: new entry - ' +
                             'UUID: {uuid}, DN: {dn}\n'.format(uuid=dn_uuid, dn=dn))

        return pw
