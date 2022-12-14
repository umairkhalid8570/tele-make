# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2022-Present Tele INC.(<https://tele.studio/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.studio/license.html/>
# 
#################################################################################

from . import models
from . import controllers

def pre_init_check(cr):
    from tele.service import common
    from tele.exceptions import Warning
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '1.0':
        raise Warning(
           'Module support Tele series 1.0 found {}.'.format(server_serie))
    return True
