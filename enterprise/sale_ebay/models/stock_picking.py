# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models, api
import re

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _action_done(self):
        res = super()._action_done()
        self._ebay_update_carrier(transfered=True)
        return res

    def _ebay_update_carrier(self, transfered=False):
        for picking in self:
            so = self.env['sale.order'].search([('name', '=', picking.origin), ('origin', 'like', 'eBay')])
            if so.order_line.filtered(lambda line: line.product_id.product_tmpl_id.ebay_use):
                call_data = {
                    'OrderLineItemID': so.client_order_ref,
                }
                if transfered:
                    call_data['Shipped'] = True
                if picking.carrier_tracking_ref and picking.carrier_id:
                    call_data['Shipment'] = {
                        'ShipmentTrackingDetails': {
                            'ShipmentTrackingNumber': picking.carrier_tracking_ref,
                            'ShippingCarrierUsed': re.sub('[^A-Za-z0-9- ]', '', picking.carrier_id.name),
                        },
                    }
                self.env['product.template'].ebay_execute("CompleteSale", call_data)
