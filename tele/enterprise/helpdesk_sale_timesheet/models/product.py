# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sla_id = fields.Many2one(
        "helpdesk.sla", string="SLA Policy",
        company_dependent=True,
        domain="[('company_id', '=', current_company_id)]")
