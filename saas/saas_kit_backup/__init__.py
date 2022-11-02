# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Tele Software Pvt. Ltd. (<https://tele.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.tele.com/license.html/>
#################################################################################

from . import models
from . import wizard
from . import controllers

def pre_init_check(cr):
    from tele.service import common
    from tele.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    # if server_serie!='14.0':raise Warning('Module support Tele series 14.0 found {}.'.format(server_serie))
    return True
