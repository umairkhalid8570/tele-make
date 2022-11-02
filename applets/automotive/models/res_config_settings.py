# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    delay_alert_contract = fields.Integer(string='Delay alert contract outdated', default=30, config_parameter='hr_automotive.delay_alert_contract')
