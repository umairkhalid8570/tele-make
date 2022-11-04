# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models


class BaseAutomation(models.Model):
    _name = 'base.automation'
    _inherit = ['studio.mixin', 'base.automation']
