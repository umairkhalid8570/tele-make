# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
from tele import models


class Task(models.Model):
    _inherit = "project.task"

    def _is_fsm_report_available(self):
        return super()._is_fsm_report_available() or self.sale_order_id
