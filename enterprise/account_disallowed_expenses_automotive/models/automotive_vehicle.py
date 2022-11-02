# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models, fields

class AutomotiveVehicle(models.Model):
    _inherit = 'automotive.vehicle'

    rate_ids = fields.One2many('automotive.disallowed.expenses.rate', 'vehicle_id', string='Disallowed Expenses Rate')


class AutomotiveDisallowedExpensesRate(models.Model):
    _name = 'automotive.disallowed.expenses.rate'
    _description = 'Vehicle Disallowed Expenses Rate'
    _order = 'date_from desc'

    rate = fields.Float(string='%', required=True)
    date_from = fields.Date(string='Start Date', required=True)
    vehicle_id = fields.Many2one('automotive.vehicle', string='Vehicle', required=True)
    company_id = fields.Many2one('res.company', string='Company', related='vehicle_id.company_id', readonly=True)
