
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields
from tele.tests import TransactionCase


class TestMedicalPatient(TransactionCase):
    def test_creation(self):
        patient = self.env["medical.patient"].create({"name": "Test Patient"})
        self.assertTrue(patient.internal_identifier)
        self.assertNotEqual(patient.internal_identifier, "/")
        patient.birth_date = fields.Date.today()
        patient.deceased_date = fields.Date.today()
        self.assertTrue(patient.is_deceased)
