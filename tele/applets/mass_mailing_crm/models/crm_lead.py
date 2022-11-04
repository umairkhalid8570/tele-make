# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _mailing_enabled = True
