# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

import tele

# ----------------------------------------------------------
# Monkey patch release to set the edition as 'enterprise'
# ----------------------------------------------------------
tele.release.version_info = tele.release.version_info[:5] + ('e',)
if '+e' not in tele.release.version:     # not already patched by packaging
    tele.release.version = '{0}+e{1}{2}'.format(*tele.release.version.partition('-'))

tele.service.common.RPC_VERSION_1.update(
    server_version=tele.release.version,
    server_version_info=tele.release.version_info)
