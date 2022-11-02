# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    registration_ids = fields.One2many('event.registration', 'partner_id', string='Event Registrations')
