# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
from tele.tests import common, new_test_user


class TestAutomotive(common.TransactionCase):

    def test_manager_create_vehicle(self):
        manager = new_test_user(self.env, "test automotive manager", groups="automotive.automotive_group_manager,base.group_partner_manager")
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["automotive.vehicle.model.brand"].create({
            "name": "Audi",
        })
        model = self.env["automotive.vehicle.model"].create({
            "brand_id": brand.id,
            "name": "A3",
        })
        self.env["automotive.vehicle"].with_user(manager).create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_car": False
        })
