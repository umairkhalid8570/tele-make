# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    intrastat = fields.Boolean(string='Intrastat member')
