
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    medical_condition_ids = fields.One2many(
        related="patient_id.medical_condition_ids",
    )
    medical_condition_count = fields.Integer(
        related="patient_id.medical_condition_count",
        string="# of Conditions",
    )
    medical_allergy_ids = fields.One2many(
        related="patient_id.medical_allergy_ids",
        domain=[("is_allergy", "=", True)],
    )
    medical_allergies_count = fields.Integer(
        related="patient_id.medical_allergies_count",
        string="# of Allergies",
    )

    medical_warning_ids = fields.One2many(
        related="patient_id.medical_warning_ids"
    )

    medical_warning_count = fields.Integer(
        related="patient_id.medical_warning_count",
        string="# of Warnings",
    )

    def action_view_medical_conditions(self):
        self.ensure_one()
        return self.patient_id.action_view_medical_conditions()

    def action_view_medical_warnings(self):
        self.ensure_one()
        return self.patient_id.action_view_medical_conditions()

    def action_view_medical_allergies(self):
        self.ensure_one()
        return self.patient_id.action_view_medical_allergies()

    def create_medical_clinical_condition(self):
        self.ensure_one()
        return self.patient_id.create_medical_clinical_condition()

    def create_allergy(self):
        self.ensure_one()
        return self.patient_id.create_allergy()
