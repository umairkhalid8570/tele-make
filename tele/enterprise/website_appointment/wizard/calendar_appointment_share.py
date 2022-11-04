# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models
from tele.osv.expression import AND


class CalendarWebsiteAppointmentShare(models.TransientModel):
    _inherit = 'calendar.appointment.share'

    def _domain_appointment_type_ids(self):
        domain = super()._domain_appointment_type_ids()
        return AND([domain, [('is_published', '!=', False)]])
