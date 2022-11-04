
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class MedicalCareplanAddPlanDefinition(models.TransientModel):
    _name = "medical.careplan.add.plan.definition"
    _inherit = "medical.add.plan.definition"
    _description = "Add a Plan Definition on a Careplan"

    def _domain_plan_definition(self):
        return [
            (
                "type_id",
                "=",
                self.env.ref("medical_workflow.medical_workflow").id,
            )
        ]

    patient_id = fields.Many2one(
        related="careplan_id.patient_id", readonly=True
    )

    careplan_id = fields.Many2one(
        comodel_name="medical.careplan", string="Care plan", required=True
    )

    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        domain=_domain_plan_definition,
        required=True,
    )

    def _get_context(self):
        return {
            "origin_model": self.careplan_id._name,
            "origin_id": self.careplan_id.id,
        }

    def _get_values(self):
        values = super(MedicalCareplanAddPlanDefinition, self)._get_values()
        values["careplan_id"] = self.careplan_id.id
        return values
