# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele.tests import tagged
from tele.applets.base.tests.common import HttpCaseWithUserDemo


@tagged('-at_install', 'post_install')
class TestUi(HttpCaseWithUserDemo):

    def test_ui(self):
        self.env.ref('approvals.approval_category_data_business_trip').write({
            'approver_ids': [(5, 0, 0), (0, 0, {'user_id': self.env.ref('base.user_admin').id})],
        })
        self.start_tour("/web", 'approvals_tour', login='admin')
