# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import _, api, fields, models
from tele.exceptions import ValidationError


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_cars_count = fields.Integer(compute="_compute_employee_cars_count", string="Cars", groups="automotive.automotive_group_manager")
    car_ids = fields.One2many(
        'automotive.vehicle', 'driver_employee_id', string='Vehicles (private)',
        groups="automotive.automotive_group_manager,hr.group_hr_user",
    )
    mobility_card = fields.Char(groups="automotive.automotive_group_user")

    def action_open_employee_cars(self):
        self.ensure_one()
        cars = self.env['automotive.vehicle.assignation.log'].search([
            ('driver_id', 'in', (self.user_id.partner_id | self.sudo().address_home_id).ids)]).mapped('vehicle_id')

        return {
            "type": "ir.actions.act_window",
            "res_model": "automotive.vehicle",
            "views": [[False, "kanban"], [False, "form"], [False, "tree"]],
            "domain": [("id", "in", cars.ids)],
            "context": dict(self._context, create=False),
            "name": "History Employee Cars",
        }

    def _compute_employee_cars_count(self):
        for employee in self:
            employee.employee_cars_count = len(employee.car_ids)

    def action_get_claim_report(self):
        self.ensure_one()
        return {
            'name': 'Claim Report',
            'type': 'ir.actions.act_url',
            'url': '/automotive/print_claim_report/%(employee_id)s' % {'employee_id': self.id},
        }

    @api.constrains('address_home_id')
    def _check_address_home_id(self):
        no_address = self.filtered(lambda r: not r.address_home_id)
        car_ids = self.env['automotive.vehicle'].sudo().search([
            ('driver_employee_id', 'in', no_address.ids),
        ])
        # Prevent from removing employee address when linked to a car
        if car_ids:
            raise ValidationError(_('Cannot remove address from employees with linked cars.'))


    def write(self, vals):
        res = super().write(vals)
        #Update car partner when it is changed on the employee
        if 'address_home_id' in vals:
            car_ids = self.env['automotive.vehicle'].sudo().search([
                ('driver_employee_id', 'in', self.ids),
                ('driver_id', 'in', self.mapped('address_home_id').ids),
            ])
            if car_ids:
                car_ids.write({'driver_id': vals['address_home_id']})
        if 'mobility_card' in vals:
            #NOTE: keeping it as a search on driver_id but we might be able to use driver_employee_id in the future
            vehicles = self.env['automotive.vehicle'].search([('driver_id', 'in', (self.user_id.partner_id | self.sudo().address_home_id).ids)])
            vehicles._compute_mobility_card()
        return res

class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    mobility_card = fields.Char(readonly=True)
