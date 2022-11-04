
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import _, api, fields, models


class MedicalCondition(models.Model):
    # FHIR Entity: Condition (https://www.hl7.org/fhir/condition.html)
    _name = "medical.condition"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _description = "Conditions"

    name = fields.Char(compute="_compute_condition_name")

    patient_id = fields.Many2one(
        comodel_name="medical.patient", string="Subject", required=True
    )  # FHIR Field: Subject

    clinical_finding_id = fields.Many2one(
        comodel_name="medical.clinical.finding", tracking=True
    )

    active = fields.Boolean(default=True, tracking=True)

    create_warning = fields.Boolean(
        compute="_compute_create_warning", store=True
    )

    is_allergy = fields.Boolean()

    criticality = fields.Selection([("low", "Low"), ("high", "High")])
    allergy_id = fields.Many2one(
        comodel_name="medical.allergy.substance", tracking=True
    )

    last_occurrence_date = fields.Date(tracking=True)

    notes = fields.Text(tracking=True)

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.condition") or "/"

    def _compute_condition_name(self):
        for rec in self:
            if rec.is_allergy:
                rec.name = _("Allergy to %s" % rec.allergy_id.name)
            else:
                rec.name = rec.clinical_finding_id.name

    @api.depends(
        "allergy_id.create_warning", "clinical_finding_id.create_warning"
    )
    def _compute_create_warning(self):
        for rec in self:
            if (
                rec.allergy_id.create_warning
                or rec.clinical_finding_id.create_warning
            ):
                rec.create_warning = True
            else:
                rec.create_warning = False

    _sql_constraints = [
        (
            "clinical_finding_id_uniq",
            "UNIQUE (clinical_finding_id, patient_id)",
            _("Clinical Finding must be unique for a patient."),
        ),
        (
            "allergy_id_uniq",
            "UNIQUE (allergy_id, patient_id)",
            _("Allergy must be unique for a patient."),
        ),
    ]

    @api.model
    def create(self, vals):
        condition = self.with_context(active_test=False).search(
            [
                ("patient_id", "=", vals.get("patient_id")),
                ("clinical_finding_id", "=", vals.get("clinical_finding_id")),
            ]
        )
        if condition:
            condition.toggle_active()
            condition.write(vals)
            return condition
        return super().create(vals)
