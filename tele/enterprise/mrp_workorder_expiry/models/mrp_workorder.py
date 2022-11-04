# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    is_expired = fields.Boolean(related='lot_id.product_expiry_alert')
