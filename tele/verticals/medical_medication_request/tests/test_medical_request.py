
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele.exceptions import ValidationError
from tele.tests.common import TransactionCase


class TestMedicalRequest(TransactionCase):
    def setUp(self):
        super(TestMedicalRequest, self).setUp()
        self.patient = self.env["medical.patient"].create(
            {"name": "Test Patient"}
        )
        self.patient2 = self.env["medical.patient"].create(
            {"name": "Test Patient2"}
        )
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.medication = self.env["product.product"].create(
            {"name": "Medication", "is_medication": True, "type": "consu"}
        )

    def test_constrains(self):
        request = self.env["medical.medication.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.medication.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["medical.medication.request"].create(
                {
                    "patient_id": self.patient2.id,
                    "medication_request_id": request.id,
                    "product_id": self.medication.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty": 1,
                }
            )

    def test_constrains_administration(self):
        request = self.env["medical.medication.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.medication.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["medical.medication.administration"].create(
                {
                    "patient_id": self.patient2.id,
                    "medication_request_id": request.id,
                    "product_id": self.medication.id,
                    "product_uom_id": self.uom_unit.id,
                    "qty": 1,
                }
            )

    def test_views(self):
        # medication request
        medication_request = self.env["medical.medication.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.medication.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
            }
        )
        medication_request._compute_medication_request_ids()
        self.assertEqual(medication_request.medication_request_count, 0)
        medication_request.with_context(
            inverse_id="active_id", model_name="medical.medication.request"
        ).action_view_request()
        # 1 medication request
        medication_request2 = self.env["medical.medication.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.medication.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
                "medication_request_id": medication_request.id,
            }
        )
        medication_request._compute_medication_request_ids()
        self.assertEqual(
            medication_request.medication_request_ids.ids,
            [medication_request2.id],
        )
        self.assertEqual(medication_request.medication_request_count, 1)
        medication_request.with_context(
            inverse_id="active_id", model_name="medical.medication.request"
        ).action_view_request()
        # 2 medication request
        medication_request3 = self.env["medical.medication.request"].create(
            {
                "patient_id": self.patient.id,
                "product_id": self.medication.id,
                "product_uom_id": self.uom_unit.id,
                "qty": 1,
                "medication_request_id": medication_request.id,
            }
        )
        medication_request._compute_medication_request_ids()
        self.assertEqual(medication_request.medication_request_count, 2)
        self.assertEqual(
            medication_request.medication_request_ids.ids.sort(),
            [medication_request2.id, medication_request3.id].sort(),
        )
        medication_request.with_context(
            inverse_id="active_id", model_name="medical.medication.request"
        ).action_view_request()
