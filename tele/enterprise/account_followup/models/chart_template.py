# -*- coding: utf-8 -*-

from tele import api, fields, models, _


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        res = super(AccountChartTemplate, self)._load(sale_tax_rate, purchase_tax_rate, company)

        if not self.env['account_followup.followup.line'].search([('company_id', '=', company.id)]):
            self.env['account_followup.followup.line'].create({
                'company_id': company.id,
                'name': _('First Reminder'),
                'delay': 15,
            })

        return res
