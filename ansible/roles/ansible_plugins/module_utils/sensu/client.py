# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.six.moves.urllib.parse import quote

from ansible.module_utils.sensu import (
    errors, http,
)


class Client:
    def __init__(self, address, username, password, namespace=None):
        self.address = address.rstrip("/")
        self.username = username
        self.password = password

        if namespace:
            self.url_template = "{0}/api/core/v2/namespaces/{1}{{0}}".format(
                self.address, quote(namespace, safe=""),
            )
        else:
            self.url_template = "{0}/api/core/v2{{0}}".format(self.address)

        self._token = None  # Login when/if required

    @property
    def token(self):
        if not self._token:
            self._token = self._login()
        return self._token

    def _login(self):
        resp = http.request(
            "GET", "{0}/auth".format(self.address), force_basic_auth=True,
            url_username=self.username, url_password=self.password,
        )

        if resp.status != 200:
            raise errors.SensuError(
                "Authentication call returned status {0}".format(resp.status),
            )

        if resp.json is None:
            raise errors.SensuError(
                "Authentication call did not return a valid JSON",
            )

        if "access_token" not in resp.json:
            raise errors.SensuError(
                "Authentication call did not return access token",
            )

        return resp.json["access_token"]

    def request(self, method, path, payload=None):
        url = self.url_template.format(path)
        headers = {"Authorization": "Bearer {0}".format(self.token)}

        return http.request(method, url, payload=payload, headers=headers)

    def get(self, path):
        return self.request("GET", path)

    def put(self, path, payload):
        return self.request("PUT", path, payload)

    def delete(self, path):
        return self.request("DELETE", path)
