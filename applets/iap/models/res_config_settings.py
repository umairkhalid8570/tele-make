# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _redirect_to_iap_account(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.env['iap.account'].get_account_url(),
        }
