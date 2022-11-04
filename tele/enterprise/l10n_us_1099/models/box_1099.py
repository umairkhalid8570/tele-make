# coding: utf-8
# Part of Tele. See LICENSE file for full copyright and licensing details.
from tele import models, fields


class Box1099(models.Model):
    _name = "l10n_us.1099_box"
    _description = "Represents a box on a 1099 box."

    name = fields.Char("Name")
