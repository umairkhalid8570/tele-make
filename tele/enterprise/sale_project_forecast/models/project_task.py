# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import api, models
from tele.osv import expression

class Task(models.Model):
    _inherit = 'project.task'

    # -------------------------------------------
    # Utils method
    # -------------------------------------------

    @api.model
    def _get_domain_compute_forecast_hours(self):
        return expression.AND([
            super()._get_domain_compute_forecast_hours(),
            [('start_datetime', '!=', False)]
        ])
