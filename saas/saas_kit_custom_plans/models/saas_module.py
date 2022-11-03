# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2021-Present Tele INC. (<https://tele.studio/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.studio/license.html/>
# 
#################################################################################

from tele import models, fields, api
from tele.exceptions import UserError, Warning
from . lib import module_lib

import logging

_logger = logging.getLogger(__name__)

class SaasModule(models.Model):
    _inherit = 'saas.module'


    @api.depends('name')
    def set_default_path(self):
        for obj in self:
            IrDefault = obj.env['ir.default'].sudo()
            applets_path = IrDefault.get('res.config.settings', 'applets_path')
            obj.applets_path = applets_path

    is_published = fields.Boolean(string="Publised", default=False)
    price = fields.Integer(string="Price")
    auto_install = fields.Boolean(string="Auto Install Module", default=True)
    applets_path = fields.Char(string="Applets Path", compute="set_default_path", store=True, readonly=False)
    order_line_id = fields.Many2one(comodel_name="sale.order.line")
    contract_id = fields.Many2one(comodel_name="saas.contract")


    def toggle_module_publish(self):
        if not self.is_published:
            """
            Check whether the module exist in the path or not.
            """
            if self.auto_install:
                res = module_lib.check_if_module([self.applets_path], self.technical_name)
                if res.get('status'):
                    self.is_published = not self.is_published                  
                elif not res.get('msg'):
                    raise UserError("You have Selected Auto install for the Module but Module does not present on the Defautl path.")
                else:
                    raise UserError(res.get('msg'))
            else:
                self.is_published = not self.is_published
        else:
            self.is_published = not self.is_published


