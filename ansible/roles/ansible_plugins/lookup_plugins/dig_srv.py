# -*- coding: utf-8 -*-
# Copyright (C) 2021 David Härdeman <david@hardeman.nu>
# Copyright (C) 2021 DebOps <https://debops.org/>
#
# Based on community.general.dig, which is:
#   (c) 2015, Jan-Piet Mens <jpmens(at)gmail.com>
#   (c) 2017 Ansible Project
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
from operator import itemgetter
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native

__metaclass__ = type

try:
    import dns.exception
    import dns.name
    import dns.resolver
    import dns.reversename
    import dns.rdataclass
    from dns.rdatatype import SRV
except ImportError:
    raise AnsibleError("dig_srv: dnspython library is not installed")


def make_rdata_dict(rdata):
    supported_types = {
        SRV: ['priority', 'weight', 'port', 'target'],
    }

    rd = {}

    if rdata.rdtype not in supported_types:
        raise AnsibleError("dig_srv: unknown rdtype returned")

    fields = supported_types[rdata.rdtype]
    for f in fields:
        val = rdata.__getattribute__(f)

        if isinstance(val, dns.name.Name):
            val = dns.name.Name.to_text(val)

        if f == "target":
            rd[f] = val.rstrip('.')
        else:
            rd[f] = val

    return rd


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        if len(terms) != 3:
            raise AnsibleError("dig_srv: three arguments expected")

        myres = dns.resolver.Resolver(configure=True)
        edns_size = 4096
        myres.use_edns(0, ednsflags=dns.flags.DO, payload=edns_size)

        domain = terms[0]
        if not domain.endswith('.'):
            domain += '.'
        default_domain = terms[1]
        default_port = terms[2]
        qtype = 'SRV'
        rdclass = dns.rdataclass.from_text('IN')

        ret = []

        try:
            answers = myres.query(domain, qtype, rdclass=rdclass)
            for rdata in answers:
                try:
                    rd = make_rdata_dict(rdata)
                    rd['owner'] = answers.canonical_name.to_text().rstrip('.')
                    rd['type'] = dns.rdatatype.to_text(rdata.rdtype)
                    rd['ttl'] = answers.rrset.ttl
                    rd['class'] = dns.rdataclass.to_text(rdata.rdclass)
                    rd['dig_srv_src'] = 'dns'
                    ret.append(rd)

                except Exception as e:
                    raise AnsibleError("dig_srv: can't parse response %s" % to_native(e))

        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            ret.append({
                "class": "IN",
                "owner": domain.rstrip('.'),
                "port": default_port,
                "priority": 0,
                "target": default_domain,
                "ttl": 0,
                "type": "SRV",
                "weight": 0,
                "dig_srv_src": "fallback"
            })
        except dns.resolver.Timeout:
            raise AnsibleError("dig_srv: timeout")
        except dns.exception.DNSException as e:
            raise AnsibleError("dig_srv: unhandled exception %s" % to_native(e))

        for r in ret:
            r.update({"target_port": r["target"] + ":" + str(r["port"])})

        # This is in reverse order of importance, i.e. least important first.
        # Note that the TTL field shows the remaining TTL when a RR is cached,
        # so sorting on that field is not a good idea.
        ret.sort(key=itemgetter("port"))
        ret.sort(key=itemgetter("target"))
        ret.sort(key=itemgetter("weight"), reverse=True)
        ret.sort(key=itemgetter("priority"))

        return ret
