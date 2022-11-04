# Part of Tele. See LICENSE file for full copyright and licensing details.
from tele.applets.point_of_sale.controllers.main import PosController
from tele import http
from tele.http import request


class PosCache(PosController):

    @http.route()
    def load_onboarding_data(self):
        super().load_onboarding_data()
        request.env["pos.cache"].refresh_all_caches()
