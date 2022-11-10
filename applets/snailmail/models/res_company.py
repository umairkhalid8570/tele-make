# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models

class Company(models.Model):
    _inherit = "res.company"

    snailmail_color = fields.Boolean(string='Color', default=True)
    snailmail_cover = fields.Boolean(string='Add a Cover Page', default=False)
    snailmail_duplex = fields.Boolean(string='Both sides', default=False)
