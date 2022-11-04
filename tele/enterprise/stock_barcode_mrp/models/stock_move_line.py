# -*- coding: utf-8 -*-

from tele import models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_fields_stock_barcode(self):
        return super()._get_fields_stock_barcode() + ['description_bom_line']
