# Part of Tele. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

import tele.tests


@tele.tests.tagged('post_install', '-at_install')
class TestUi(tele.tests.HttpCase):
    def test_ui(self):
        self.start_tour("/web", 'helpdesk_tour', login="admin")
