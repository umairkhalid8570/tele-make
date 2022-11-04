# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models


class Forecast(models.Model):

    _inherit = 'planning.slot'

    order_line_id = fields.Many2one('sale.order.line', string='Sales Order Line', related="task_id.sale_line_id", store=True, readonly=False)
