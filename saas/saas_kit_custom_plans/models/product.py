# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2022-Present Tele INC.(<https://tele.studio/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.studio/license.html/>
# 
#################################################################################

from tele import models, fields, api
from tele.exceptions import UserError, Warning

import logging

_logger = logging.getLogger(__name__)

class SaasModuleProduct(models.Model):
    _inherit = 'product.product'

    is_saas_module = fields.Boolean(string="For Saas Module", default=False)

    @api.onchange('is_saas_module')
    def change_saas_module(self):
        if self.is_saas_module:
            self.saas_plan_id = None
            self.is_user_pricing = False
