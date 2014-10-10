# (c) 2014, Maciej Delmanowski <drybjed@gmail.com>
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
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import struct
import socket
from ansible import errors


# ---- General IP address functions ----

def ipaddr(string):
    ''' Check if string is an IP address '''
    if ipv6(string):
        return True
    elif ipv4(string):
        return True
    else:
        return False


# ---- IPv4 address functions ----

def ipv4(string):
    ''' Check if string is an IPv4 address '''
    try:
        (address, mask) = string.split('/')
    except:
        address = string
        mask = False
    try:
        socket.inet_pton(socket.AF_INET, address)
        if mask:
            assert int(mask) >= 0 and int(mask) <= 32
    except:
        return False
    return True

def ipv4_to_int(addr):
    ''' Convert IPv4 address to integer '''
    if ipv4(addr):
        try:
            (address, mask) = addr.split('/')
        except:
            address = addr
            mask = False
        try:
            _str = socket.inet_pton(socket.AF_INET, address)
            _ret = int(struct.unpack("!I", _str)[0])
        except Exception, e:
            raise errors.AnsibleFilterError('Illegal IPv4 address: %s' % addr)
        if mask:
            return str(_ret) + '/' + str(mask)
        else:
            return str(_ret)

def int_to_ipv4(integer):
    ''' Convert integer to IPv4 address '''
    if ipv4(integer):
        return integer
    else:
        try:
            (addr, mask) = integer.split('/')
        except:
            addr = integer
            mask = False
        try:
            assert int(addr) > 0
        except Exception, e:
            raise errors.AnsibleFilterError('Not an integer: %s' % integer)
        if mask:
            try:
                assert int(mask) >= 0 and int(mask) <= 32
            except:
                try:
                    mask = ipv4_cidr(mask)
                    assert int(mask) >= 0 and int(mask) <= 32
                except Exception, e:
                    raise errors.AnsibleFilterError('CIDR mask outside of range: %s' % integer)
        try:
            _str = socket.inet_ntop(socket.AF_INET, struct.pack("!I", int(addr)))
        except Exception, e:
            raise errors.AnsibleFilterError('Outside of IPv4 address space: %s' % addr)
        if mask:
            return str(_str + '/' + str(mask))
        else:
            return str(_str)

def ipv4_netmask(cidr):
    ''' Convert CIDR suffix to IPv4 netmask '''
    try:
        assert int(cidr) > 0
        _str = socket.inet_ntop(socket.AF_INET, struct.pack(">I", (0xffffffff << (32 - int(cidr))) & 0xffffffff))
    except Exception, e:
        raise errors.AnsibleFilterError('Outside of IPv4 CIDR space: %s' % cidr)
    return str(_str)

def ipv4_cidr(mask):
    ''' Convert IPv4 netmask to CIDR suffix '''
    _binary_str = ''
    try:
        for octet in mask.split('.'):
            _binary_str += bin(int(octet))[2:].zfill(8)
    except Exception, e:
        raise errors.AnsibleFilterError('Illegal IPv4 netmask: %s' % mask)
    return str(len(_binary_str.rstrip('0')))


# ---- IPv6 address functions ----

def ipv6(string):
    ''' Check if string is an IPv6 address '''
    try:
        (address, mask) = string.split('/')
    except:
        address = string
        mask = False
    try:
        socket.inet_pton(socket.AF_INET6, address)
        if mask:
            assert int(mask) >= 0 and int(mask) <= 128
    except:
        return False
    return True

def ipv6_to_int(addr):
    ''' Convert IPv6 address to integer '''
    if ipv4(addr):
        tempaddr = ipv4_to_int(addr)
        try:
            (addr, mask) = tempaddr.split('/')
            mask = int(128) - int(mask)
        except:
            addr = tempaddr
            mask = False
        if mask:
            addr = int_to_ipv6(str(addr) + '/' + str(mask))
        else:
            addr = int_to_ipv6(addr)
    if ipv6(addr):
        try:
            (address, mask) = addr.split('/')
        except:
            address = addr
            mask = False
        try:
            _str = socket.inet_pton(socket.AF_INET6, address)
            a, b = struct.unpack("!2Q", _str)
            _ret = (a << 64) | b
        except Exception, e:
            raise errors.AnsibleFilterError('Illegal IPv6 address: %s' % addr)
        if mask:
            return str(_ret) + '/' + str(mask)
        else:
            return str(_ret)
    else:
            raise errors.AnsibleFilterError('Illegal IPv6 address: %s' % addr)

def int_to_ipv6(integer):
    ''' Convert integer to IPv6 address '''
    if ipv6(integer):
        return integer
    else:
        if ipv4(integer):
            tempaddr = ipv4_to_int(integer)
            try:
                (addr, mask) = tempaddr.split('/')
                mask = int(128) - int(mask)
            except:
                addr = tempaddr
                mask = False
        else:
            try:
                (addr, mask) = integer.split('/')
            except:
                addr = integer
                mask = False
        try:
            assert int(addr) >= 0
        except Exception, e:
            raise errors.AnsibleFilterError('Not an integer: %s' % integer)
        if mask:
            try:
                assert int(mask) >= 0 and int(mask) <= 128
            except Exception, e:
                raise errors.AnsibleFilterError('CIDR mask outside of range: %s' % integer)
        try:
            a = int(addr) >> 64
            b = int(addr) & ((1 << 64) - 1)
            _str = socket.inet_ntop(socket.AF_INET6, struct.pack("!2Q", a, b))
        except Exception, e:
            raise errors.AnsibleFilterError('Outside of IPv6 address space: %s' % addr)
        if mask:
            return str(_str + '/' + str(mask))
        else:
            return str(_str)

def wrap_ipv6(string):
    ''' Wrap IPv6 address into square backets '''
    if ipv6(string):
        try:
            (address, mask) = string.split('/')
        except:
            address = string
            mask = False
        if int(mask):
            return str('[' + address + ']/' + mask)
        else:
            return str('[' + address + ']')
    else:
        return string


# ---- Ansible filters ----

class FilterModule(object):
    ''' IPv4 address and netmask manipulation filters '''

    def filters(self):
        return {

            # IP address manipulation
            'ipaddr': ipaddr,
            'ipv4': ipv4,
            'ipv6': ipv6,
            'wrap_ipv6': wrap_ipv6,

            # IPv4 address conversion
            'from_ipv4': ipv4_to_int,
            'to_ipv4': int_to_ipv4,

            # IPv6 address conversion
            'from_ipv6': ipv6_to_int,
            'to_ipv6': int_to_ipv6,

            # IPv4 netmask conversion
            'ipv4_netmask': ipv4_netmask,
            'ipv4_cidr': ipv4_cidr
        }

