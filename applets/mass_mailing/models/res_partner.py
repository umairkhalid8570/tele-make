# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models


class Partner(models.Model):
    _inherit = 'res.partner'
    _mailing_enabled = True
