# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'voip.queue.mixin']
