# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2022-Present Tele INC.(<https://tele.studio/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.studio/license.html/>
# 
#################################################################################

from tele import fields, api, models
from tele.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

APPS_VIEW = [
    ('normal', 'Normal'),
    ('category', 'Catagorical')
]

Nature = [
    ('per_month', 'Per Month'),
    ('per_user', 'Per User')
]

RECURRING_RULE = [
    ('daily', 'Day(s)'),
    ('weekly', 'Week(s)'),
    ('monthly', 'Month(s)'),
    ('monthlylastday', 'Month(s) last day'),
    ('yearly', 'Year(s)')
]

class SaasConfig(models.TransientModel):
    _inherit = 'res.config.settings'


    is_tele_version = fields.Boolean(string="Provide Version Selection", default=True)
    is_users = fields.Boolean(string="Provide User Selection", default=True)
    apps_view = fields.Selection(selection=APPS_VIEW, string="Apps View", default='normal')
    max_users = fields.Integer(string="Max Users")
    is_free_users = fields.Boolean(string="Provide free Users")
    free_users = fields.Integer(string="Free Users")
    costing_nature = fields.Selection(selection=Nature, string="Select Nature of Apps Costing")
    user_cost = fields.Integer(string="Per User Cost")
    due_user_cost = fields.Integer(string="Due User Cost")
    applets_path = fields.Char(string="Default Addons Path")
    recurring_rule_type = fields.Selection(selection=RECURRING_RULE, string="Default Recurring Type", default="monthly")
    is_multi_server = fields.Boolean(string="Provide Multi Server", default=False)
    reminder_period = fields.Integer(string="Reminder Starts")
    is_reminder_period = fields.Boolean(string="Enable Reminder")




    def set_values(self):
        super(SaasConfig, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', 'is_tele_version', self.is_tele_version)
        IrDefault.set('res.config.settings', 'is_users', self.is_users)
        IrDefault.set('res.config.settings', 'apps_view', self.apps_view)
        IrDefault.set('res.config.settings', 'max_users', self.max_users)
        IrDefault.set('res.config.settings', 'is_free_users', self.is_free_users)
        IrDefault.set('res.config.settings', 'free_users', self.free_users)
        IrDefault.set('res.config.settings', 'costing_nature', self.costing_nature)
        IrDefault.set('res.config.settings', 'user_cost', self.user_cost)
        IrDefault.set('res.config.settings', 'due_user_cost', self.due_user_cost)
        IrDefault.set('res.config.settings', 'applets_path', self.applets_path)
        IrDefault.set('res.config.settings', 'recurring_rule_type', self.recurring_rule_type)
        IrDefault.set('res.config.settings', 'is_multi_server', self.is_multi_server)
        IrDefault.set('res.config.settings', 'reminder_period', self.reminder_period)
        IrDefault.set('res.config.settings', 'is_reminder_period', self.is_reminder_period)
        return True

    def get_values(self):
        res = super(SaasConfig, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update(
            {
                'is_tele_version': IrDefault.get('res.config.settings', 'is_tele_version'),
                'is_users': IrDefault.get('res.config.settings', 'is_users'),
                'apps_view': IrDefault.get('res.config.settings', 'apps_view') or 'normal',
                'max_users': IrDefault.get('res.config.settings', 'max_users') or -1,
                'is_free_users': IrDefault.get('res.config.settings', 'is_free_users'),
                'free_users': IrDefault.get('res.config.settings', 'free_users'),
                'costing_nature': IrDefault.get('res.config.settings', 'costing_nature') or 'per_month',
                'user_cost': IrDefault.get('res.config.settings', 'user_cost') or 1,
                'due_user_cost': IrDefault.get('res.config.settings', 'due_user_cost') or 1,
                'applets_path': IrDefault.get('res.config.settings', 'applets_path') or '/opt/tele/applets',
                'recurring_rule_type': IrDefault.get('res.config.settings', 'recurring_rule_type') or 'monthly',
                'is_multi_server': IrDefault.get('res.config.settings', 'is_multi_server') or False,
                'reminder_period': IrDefault.get('res.config.settings', 'reminder_period') or 3,
                'is_reminder_period': IrDefault.get('res.config.settings', 'is_reminder_period')
            }
        )
        return res

