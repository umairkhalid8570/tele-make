# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele.applets.appointment.controllers.calendar import AppointmentController
from tele.osv.expression import AND


class WebsiteAppointmentController(AppointmentController):
    def _get_employee_appointment_type_domain(self, employee):
        domain = super()._get_employee_appointment_type_domain(employee)
        return AND([domain, [('website_published', '=', True)]])
