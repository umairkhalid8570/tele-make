# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import api, models


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['sepa_direct_debit'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res
