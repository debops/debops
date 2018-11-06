# (c) 2015, Hartmut Goebel <h.goebel@crazy-compilers.com>
# Based on `runner/lookup_plugins/items.py` for Ansible
#   (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Debops.
# This file is NOT part of Ansible yet.
#
# Debops is free software: you can redistribute it and/or modify
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
# along with Debops.  If not, see <https://www.gnu.org/licenses/>.
'''

This file implements the `with_lists` lookup filter for Ansible. In
differenceto `with_items`, this one does *not* flatten the lists passed to.

Example:

  - debug: msg="{{item.0}} -- {{item.1}} -- {{item.2}}"
    with_lists:
     - ["General", "Verbosity", "0"]
     - ["Mapping", "Nobody-User", "nobody"]
     - ["Mapping", "Nobody-Group", "nogroup"]

Output (shortend):
    "msg": "General -- Verbosity -- 0"
    "msg": "Mapping -- Nobody-User -- nobody"
    "msg": "Mapping -- Nobody-Group -- nogroup"
'''

import ansible.utils as utils
import ansible.errors as errors

try:
    from ansible.plugins.lookup import LookupBase
except ImportError:
    LookupBase = object


class LookupModule(LookupBase):

    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):
        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject)

        if not isinstance(terms, (list, set)):
            raise errors.AnsibleError("with_list expects a list or a set")

        for i, elem in enumerate(terms):
            if not isinstance(elem, (list, tuple)):
                raise errors.AnsibleError(
                        "with_list expects a list (or a set) of lists"
                        " or tuples, but elem %i is not")

        return terms
