
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import _, fields, models
from tele.exceptions import Warning as Warn


class MedicalAddPlanDefinition(models.TransientModel):
    _name = "medical.add.plan.definition"
    _description = "Add Plan Definition"

    def _domain_plan_definition(self):
        return [
            (
                "type_id",
                "=",
                self.env.ref("medical_workflow.medical_workflow").id,
            )
        ]

    patient_id = fields.Many2one(
        comodel_name="medical.patient", string="Patient", required=True
    )

    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        domain=_domain_plan_definition,
        required=True,
    )

    def _get_values(self):
        return {
            "patient_id": self.patient_id.id,
            "name": self.plan_definition_id.name,
        }

    def _get_context(self):
        return {
            "origin_model": self.patient_id._name,
            "origin_id": self.patient_id.id,
        }

    def _run(self):
        self.ensure_one()
        vals = self._get_values()
        ctx = self._get_context()
        ctx.update(self.env.context)
        return self.plan_definition_id.with_context(
            ctx
        ).execute_plan_definition(vals)

    def run(self):
        res = self._run()
        if not res:
            raise Warn(_("No requests were created"))
