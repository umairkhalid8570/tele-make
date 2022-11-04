# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
from tele.tests import common, new_test_user
from tele import fields


class TestAutomotive(common.TransactionCase):

    def test_search_renewal(self):
        """
            Should find the car with overdue contract or renewal due soon
        """
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["automotive.vehicle.model.brand"].create({
            "name": "Audi",
        })
        model = self.env["automotive.vehicle.model"].create({
            "brand_id": brand.id,
            "name": "A3",
        })
        car_1 = self.env["automotive.vehicle"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_car": False
        })

        car_2 = self.env["automotive.vehicle"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_car": False
        })
        Log = self.env['automotive.vehicle.log.contract']
        log = Log.create({
            'vehicle_id': car_2.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=10)
        })
        res = self.env["automotive.vehicle"].search([('contract_renewal_due_soon', '=', True), ('id', '=', car_2.id)])
        self.assertEqual(res, car_2)

        log = Log.create({
            'vehicle_id': car_1.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=-10)
        })
        res = self.env["automotive.vehicle"].search([('contract_renewal_overdue', '=', True), ('id', '=', car_1.id)])
        self.assertEqual(res, car_1)
