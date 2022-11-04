# -*- coding: utf-8 -*-
from tele import models
from tele.http import request


class Website(models.Model):
    _inherit = 'website'

    def sale_reset(self):
        request.session.pop('pending_coupon_code')
        return super().sale_reset()
