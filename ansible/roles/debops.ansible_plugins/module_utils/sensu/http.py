# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.module_utils.urls import open_url

from ansible.module_utils.sensu import (
    errors, debug,
)


class Response:
    def __init__(self, status, data):
        self.status = status
        self.data = data
        self._json = None

    @property
    def json(self):
        if self._json is None:
            try:
                self._json = json.loads(self.data)
            except ValueError:  # Cannot use JSONDecodeError here (python 2)
                self._json = None

        return self._json


def request(method, url, payload=None, data=None, headers=None, **kwargs):
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":"))
        headers = dict(headers or {}, **{"content-type": "application/json"})

    try:
        raw_resp = open_url(
            method=method, url=url, data=data, headers=headers, **kwargs
        )
        resp = Response(raw_resp.getcode(), raw_resp.read())
        debug.log_request(method, url, payload, resp)
        return resp
    except HTTPError as e:
        # This is not an error, since client consumers might be able to
        # work around/expect non 20x codes.
        resp = Response(e.code, e.reason)
        debug.log_request(method, url, payload, resp)
        return resp
    except URLError as e:
        debug.log_request(method, url, payload, comment=e.reason)
        raise errors.HttpError(
            "{0} request failed: {1}".format(method, e.reason),
        )
