# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2021-Present Tele INC. (<https://tele.studio/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.studio/license.html/>
# 
#################################################################################

from tele import api, models, fields
from tele.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class CustomDomainWizard(models.TransientModel):
    _name = "custom.domain.wizard"

    name = fields.Char(string="Domain Name")
    is_ssl_enable = fields.Boolean(string="Enable SSL/HTTPS")

    def save_domain(self):
        contract = self.env['saas.contract'].sudo().browse(self.env.context.get('instance_id'))
        contract.add_custom_domain(self.name, self.is_ssl_enable)