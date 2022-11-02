# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

import tele.tests


@tele.tests.tagged('post_install', '-at_install')
class TestRoutes(tele.tests.HttpCase):

    def test_01_web_session_destroy(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.authenticate('demo', 'demo')
        res = self.opener.post(url=base_url + '/web/session/destroy', json={})
        self.assertEqual(res.status_code, 200)
