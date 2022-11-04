# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

import logging

from tele import http
from tele.http import request
from tele.applets.payment_adyen.controllers.main import AdyenController

_logger = logging.getLogger(__name__)


class PosRestaurantAdyenController(AdyenController):

    @http.route()
    def adyen_notification(self, **post):
        if post.get('eventCode') in ['CAPTURE', 'AUTHORISATION_ADJUSTMENT'] and post.get('success') != 'true':
                _logger.warning('%s for transaction_id %s failed', post.get('eventCode'), post.get('originalReference'))
        return super(PosRestaurantAdyenController, self).adyen_notification(**post)
