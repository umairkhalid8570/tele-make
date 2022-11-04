# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from tele import api, fields, models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    encounter_ids = fields.One2many(
        comodel_name="medical.encounter", inverse_name="patient_id"
    )
    encounter_count = fields.Integer(compute="_compute_encounter_count")

    @api.depends("encounter_ids")
    def _compute_encounter_count(self):
        for record in self:
            record.encounter_count = len(record.encounter_ids)

    def action_view_encounter_ids(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_administration_encounter.medical_encounter_action"
        ).read()[0]
        action["domain"] = [("patient_id", "=", self.id)]
        return action
