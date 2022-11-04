# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from . import models

def post_init(cr, registry):
    from tele import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    env['project.project'].search([('is_fsm', '=', True)]).write({
        'allow_billable': True,
        'allow_material': True,
        'allow_timesheets': True,
        'timesheet_product_id': env.ref('sale_timesheet.time_product')
    })
