# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = """
options:
  namespace:
    description:
      - RBAC namespace to operate in. If this is not set the value of the
        SENSU_NAMESPACE environment variable will be used.
    type: str
    default: default
"""
