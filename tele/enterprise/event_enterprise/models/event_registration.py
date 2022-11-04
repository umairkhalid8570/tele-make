# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    # store it to be able to group_by (event_begin_date in cohort view)
    event_begin_date = fields.Datetime(store=True)
