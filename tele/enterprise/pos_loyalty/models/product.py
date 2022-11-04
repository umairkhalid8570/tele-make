# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models, _
from tele.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            product_in_reward = self.env['loyalty.reward'].sudo().search(['&', ('loyalty_program_id', '!=', False),
                                                                    '|', ('gift_product_id', 'in', self.ids),
                                                                    ('discount_product_id', 'in', self.ids)], limit=1)
            if product_in_reward:
                raise ValidationError(_("The product cannot be archived because it's used in a point of sales loyalty program."))
        return super().write(vals)
