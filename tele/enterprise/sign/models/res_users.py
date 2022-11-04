# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    sign_signature = fields.Binary(string="Digital Signature", groups="base.group_system")
    sign_initials = fields.Binary(string="Digitial Initials", groups="base.group_system")
