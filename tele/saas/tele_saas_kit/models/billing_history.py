# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2021-Present Tele INC. (<https://tele.studio/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.studio/license.html/>
#
#################################################################################

import logging
from tele import fields, models
from tele.exceptions import Warning
_logger = logging.getLogger(__name__)

class BillingHistory(models.Model):
    _name = 'user.billing.history'

    name = fields.Char(string="Entry Name")
    date = fields.Date(string="Date")
    cycle_number = fields.Char(string="Cycle")
    due_users = fields.Integer(string="Due Users")
    free_users = fields.Integer(string="Free Users")
    puchased_users = fields.Integer(string="Purchased Users")
    due_users_price = fields.Float(string="Due Users Price")
    puchase_users_price = fields.Float(string="Purchase Users Price")
    is_invoiced = fields.Boolean(string="Invoiced")
    final_price = fields.Float(string="Final User's Price")
    contract_id = fields.Many2one(comodel_name="saas.contract", string="Contract ID")
