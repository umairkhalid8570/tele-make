# coding: utf-8
from tele import _
from tele.exceptions import UserError

from tele.applets.website_sale.controllers.main import WebsiteSale

class WebsiteSaleAvatax(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        res = super(WebsiteSaleAvatax, self)._get_shop_payment_values(order, **kwargs)
        res['on_payment_step'] = True

        if order.fiscal_position_id.is_avatax:
            try:
                order.button_update_avatax()
            except UserError as e:
                res['errors'].append(
                    (_("Validation Error"),
                     _("This address does not appear to be valid. Please make sure it has been filled in correctly. Error details: %s", e))
                )

        return res
