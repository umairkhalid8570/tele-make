# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2021-Present Tele INC. (<https://tele.studio/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.studio/license.html/>
# 
#################################################################################

from tele import fields, models, api
from tele.exceptions import UserError, Warning, ValidationError
from . lib import saas_client_db
import logging

_logger = logging.getLogger(__name__)

MODULE_STATUS = [('installed', "Installed"), 
                ('uninstalled', "Not Installed")]

class ModuleStatus(models.Model):
    _name = 'saas.module.status'
    _description = 'Class for managing module instalation status in client record.'

    module_id = fields.Many2one(comodel_name="saas.module", string="Module")
    technical_name = fields.Char(string="Technical Name", related="module_id.technical_name", readonly=True)
    status = fields.Selection(selection=MODULE_STATUS, default="uninstalled")
    client_id = fields.Many2one(comodel_name="saas.client", string="SaaS Client")

    def install_module(self):
        for obj in self:
            data = dict(
                operation="install",
                tele_url=obj.client_id.client_url,
                tele_username="admin",
                tele_password="admin",
                database_name=obj.client_id.database_name,
                modules_list=[obj.technical_name],
            )
            response = saas_client_db.create_saas_client(**data)
            if not response.get("modules_installation", False):
                missed_list = ", ".join(response.get('modules_missed'))
                raise UserError("Could't Install the following modules:\n{}".format(missed_list))
            else:
                obj.status = "installed"

    def uninstall_module(self):
        pass

    def upgrade_module(self):
        pass