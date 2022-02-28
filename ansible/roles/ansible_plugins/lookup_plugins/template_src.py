# (c) 2015, Robert Chady <rchady@sitepen.com>
# Based on `runner/lookup_plugins/file.py` for Ansible
#   (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
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

import os

try:
    import debops
    debops_version = debops.__version__.__version__
    conf_section = 'override_paths'
    conf_key = 'templates_path'
except AttributeError:
    try:
        from debops import *
        from debops.cmds import *
        debops_version = '2.3.0'
        conf_section = 'paths'
        conf_key = 'template-paths'
    except ImportError:
        pass
except ModuleNotFoundError:
    conf_section = ''
    conf_key = ''
    pass

try:
    from ansible.plugins.lookup import LookupBase
except ImportError:
    LookupBase = object

from distutils.version import LooseVersion
from ansible import __version__ as __ansible_version__

'''

This file implements the `template_src` lookup filter for Ansible. In
difference to the `template` filter, this searches values based on the
`template-paths` variable (colon separated) as configured in DebOps.

NOTE: This means this filter relies on DebOps.

'''

__author__ = "Robert Chady <rchady@sitepen.com>"
__copyright__ = "Copyright 2015 by Robert Chady <rchady@sitepen.com>"
__license__ = "GNU General Public LIcense version 3 (GPL v3) or later"


if LooseVersion(__ansible_version__) < LooseVersion("2.0"):
    from ansible import utils, errors

    class LookupModule(object):

        def __init__(self, basedir, *args, **kwargs):
            self.basedir = basedir

        def run(self, terms, inject=None, **kwargs):

            terms = utils.listify_lookup_plugin_terms(
                    terms, self.basedir, inject)
            ret = []
            config = {}
            places = []

            # this can happen if the variable contains a string,
            # strictly not desired for lookup plugins, but users may
            # try it, so make it work.
            if not isinstance(terms, list):
                terms = [terms]

            try:
                project_config = debops.config.Configuration()
                project_dir = debops.projectdir.ProjectDir(
                        config=project_config)
                project_root = project_dir.path
                config = project_dir.config.get(['views', 'system'])
            except NameError:
                try:
                    project_root = find_debops_project(required=False)
                    config = read_config(project_root)
                except NameError:
                    pass
            except NotADirectoryError:
                # This is not a DebOps project directory, so continue as normal
                pass

            if conf_section in config and conf_key in config[conf_section]:
                custom_places = (
                        config[conf_section][conf_key].split(':'))
                for custom_path in custom_places:
                    if os.path.isabs(custom_path):
                        places.append(custom_path)
                    else:
                        places.append(os.path.join(
                            project_root, custom_path))

            for term in terms:
                if '_original_file' in inject:
                    relative_path = (
                            utils.path_dwim_relative(
                                inject['_original_file'], 'templates',
                                '', self.basedir, check=False))
                    places.append(relative_path)
                for path in places:
                    template = os.path.join(path, term)
                    if template and os.path.exists(template):
                        ret.append(template)
                        break
                else:
                    raise errors.AnsibleError(
                            "could not locate file in lookup: %s"
                            % term)

            return ret

else:
    from ansible.errors import AnsibleError
    from ansible.plugins.lookup import LookupBase

    class LookupModule(LookupBase):

        def run(self, terms, variables=None, **kwargs):
            ret = []
            config = {}
            places = []

            # this can happen if the variable contains a string,
            # strictly not desired for lookup plugins, but users may
            # try it, so make it work.
            if not isinstance(terms, list):
                terms = [terms]

            try:
                project_config = debops.config.Configuration()
                project_dir = debops.projectdir.ProjectDir(
                        config=project_config)
                project_root = project_dir.path
                config = project_dir.config.get(['views', 'system'])
            except NameError:
                try:
                    project_root = find_debops_project(required=False)
                    config = read_config(project_root)
                except NameError:
                    pass
            except NotADirectoryError:
                # This is not a DebOps project directory, so continue as normal
                pass

            if conf_section in config and conf_key in config[conf_section]:
                custom_places = (
                        config[conf_section][conf_key].split(':'))
                for custom_path in custom_places:
                    if os.path.isabs(custom_path):
                        places.append(custom_path)
                    else:
                        places.append(os.path.join(
                            project_root, custom_path))

            for term in terms:
                if 'role_path' in variables:
                    relative_path = (
                            self._loader.path_dwim_relative(
                                variables['role_path'], 'templates',
                                ''))
                    places.append(relative_path)
                for path in places:
                    template = os.path.join(path, term)
                    if template and os.path.exists(template):
                        ret.append(template)
                        break
                else:
                    raise AnsibleError(
                            "could not locate file in lookup: %s"
                            % term)

            return ret
