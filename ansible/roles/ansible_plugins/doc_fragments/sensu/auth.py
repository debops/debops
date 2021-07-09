# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = """
options:
  auth:
    description:
      - Authentication parameters. Can define each of them with ENV as well.
    type: dict
    suboptions:
      user:
        description:
          - The username to use for connecting to the Sensu API.
            If this is not set the value of the SENSU_USER environment
            variable will be checked.
          - This parameter is ignored if the I(auth.api_key) parameter is set.
        type: str
        default: admin
      password:
        description:
          - The Sensu user's password.
            If this is not set the value of the SENSU_PASSWORD environment
            variable will be checked.
          - This parameter is ignored if the I(auth.api_key) parameter is set.
        type: str
        default: P@ssw0rd!
      url:
        description:
          - Location of the Sensu backend API.
            If this is not set the value of the SENSU_URL environment variable
            will be checked.
        type: str
        default: http://localhost:8080
      api_key:
        description:
          - The API key that should be used when authenticating. If this is
            not set, the value of the SENSU_API_KEY environment variable will
            be checked.
          - This replaces I(auth.user) and I(auth.password) parameters.
          - For more information about the API key, refer to the official
            Sensu documentation at
            U(https://docs.sensu.io/sensu-go/latest/guides/use-apikey-feature/).
        type: str
        version_added: "1.3"
"""
