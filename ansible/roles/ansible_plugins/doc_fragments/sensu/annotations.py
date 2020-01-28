# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = """
options:
  annotations:
    description:
      - Custom metadata fields with fewer restrictions, as key/value pairs.
      - These are preserved by Sensu but not accessible as tokens or
        identifiers, and are mainly intended for use with external tools.
    type: dict
"""
