# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2021-Present Tele INC. (<https://tele.studio/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.studio/license.html/>
# 
#################################################################################

from tele import fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one(comodel_name='saas.contract', string='SaaS Contract')