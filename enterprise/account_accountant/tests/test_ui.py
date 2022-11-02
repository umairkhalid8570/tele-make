# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

import tele.tests


@tele.tests.tagged('-at_install', 'post_install')
class TestUi(tele.tests.HttpCase):
    def test_accountant_tour(self):
        self.start_tour("/web", 'account_accountant_tour', login="admin")
