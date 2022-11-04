# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele.tests.common import HttpCase
from tele.applets.sale_product_configurator.tests.common import TestProductConfiguratorCommon
from tele.tests import tagged


@tagged('post_install', '-at_install')
class TestUi(HttpCase, TestProductConfiguratorCommon):

    def test_01_admin_shop_custom_attribute_value_tour(self):
        # fix runbot, sometimes one pricelist is chosen, sometimes the other...
        pricelists = self.env['website'].get_current_website().get_current_pricelist() | self.env.ref('product.list0')
        self._create_pricelist(pricelists)
        self.start_tour("/", 'a_shop_custom_attribute_value', login="admin")
