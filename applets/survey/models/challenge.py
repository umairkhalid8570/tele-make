# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models, fields


class Challenge(models.Model):
    _inherit = 'recognition.challenge'

    challenge_category = fields.Selection(selection_add=[
        ('certification', 'Certifications')
    ], ondelete={'certification': 'set default'})
