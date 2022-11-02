# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Tele Software Pvt. Ltd. (<https://tele.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.com/license.html/>
# 
#################################################################################

from tele import fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one(comodel_name='saas.contract', string='SaaS Contract')