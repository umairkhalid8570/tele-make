# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models

class AutomotiveVehicleLogContract(models.Model):
    _inherit = 'automotive.vehicle.log.contract'

    purchaser_employee_id = fields.Many2one(
        related='vehicle_id.driver_employee_id',
        string='Driver (Employee)',
    )
