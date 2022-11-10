# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models
from tele.tools import populate


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _populate_get_product_factories(self):
        """Populate the invoice_policy of product.product & product.template models."""
        return super()._populate_get_product_factories() + [
            ("invoice_policy", populate.randomize(['order', 'delivery'], [5, 5]))]
