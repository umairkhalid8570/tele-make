# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Tele Software Pvt. Ltd. (<https://tele.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.tele.com/license.html/>
# 
#################################################################################

from tele import fields, models, api

class SaasModule(models.Model):
    _name = 'saas.module'
    _description = 'Class for creating Modules that one wishes to provide as a service.'

    name = fields.Char(string="Name", required=True)
    image = fields.Binary(string='Image')
    technical_name = fields.Char(string="Technical Name", required=True)
    categ_id = fields.Many2one(comodel_name="saas.module.category", string="Module Category")