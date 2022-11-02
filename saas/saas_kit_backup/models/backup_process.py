# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Tele Software Pvt. Ltd. (<https://tele.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.com/license.html/>
#
#################################################################################

from tele import fields, api, models


import logging

_logger = logging.getLogger(__name__)


class SaasBackupProcess(models.Model):
    _inherit = 'backup.process'

    saas_client_id = fields.Many2one(comodel_name='saas.client', string="Linked Client")

    
    def create_backup_request(self):
        if self.saas_client_id:
            self.saas_client_id.get_backup()
        else:
            res = super(SaasBackupProcess, self).create_backup_request()
            return res


