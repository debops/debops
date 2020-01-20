# -*- coding: utf-8 -*-
# Copyright: (c) 2019, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import tempfile
from datetime import datetime


DEBUG = os.environ.get("SENSU_ANSIBLE_DEBUG", "").lower() in ["yes", "true"]


def log(message, *args, **kwargs):
    """
    Log message to a file (/tmp/sensu-ansible.log) at remote target

    Sensu API returns fairly modest error messages (e.g. when PUT payload contains
    unsupported parameter, the error message won't tell you which one) and that
    makes it difficult to debug. For that reason we decided to support at least
    the most primitive type of logging: write to /tmp/sensu-ansible.log file.
    Beware the log file resides on Ansible target and not host because this is
    where the module gets executed.

    This function won't do anything unless target has environment variable
    SENSU_ANSIBLE_DEBUG set to "yes". When troubleshooting, just set the env
    variable in the playbook.
    """
    if DEBUG:
        with open(os.path.join(tempfile.gettempdir(), "sensu-ansible.log"), "a") as f:
            f.write("[{0}]: {1}\n".format(datetime.utcnow(), message.format(*args, **kwargs)))


def log_request(method, url, payload, resp=None, comment=None):
    """Log API request and response"""
    if DEBUG:
        if resp:
            code, data = resp.status, resp.data
        else:
            code = data = "?"
        fmt = "{0} {1} {2}\nPAYLOAD:{3}\nRESPONSE:{4}\nCOMMENT:{5}"
        log(fmt, code, method, url, payload, data, comment)
