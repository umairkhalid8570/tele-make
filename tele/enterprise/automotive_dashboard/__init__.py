# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
from tele.api import Environment, SUPERUSER_ID

def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env.ref('automotive.automotive_costs_reporting_action').write({'view_mode': 'graph,pivot'})