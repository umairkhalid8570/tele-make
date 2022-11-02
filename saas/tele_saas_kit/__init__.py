# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Tele Software Pvt. Ltd. (<https://tele.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.com/license.html/>
# 
#################################################################################

from . import models
from . import wizards
from . import controllers

def pre_init_check(cr):
    from tele.service import common
    from tele.exceptions import Warning
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '15.0':
        raise Warning(
           'Module support Tele series 15.0 found {}.'.format(server_serie))
    return True
