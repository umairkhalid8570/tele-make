# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from tele import api, fields, models


class MedicalEvent(models.AbstractModel):
    # FHIR Entity: Event (https://www.hl7.org/fhir/event.html)
    _name = "medical.event"
    _description = "Medical event"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _order = "create_date DESC"

    @api.model
    def _get_states(self):
        return [
            ("preparation", "Preparation"),
            ("in-progress", "In progress"),
            ("suspended", "Suspended"),
            ("aborted", "Aborted"),
            ("completed", "Completed"),
            ("entered-in-error", "Entered in error"),
            ("unknown", "Unknown"),
        ]

    name = fields.Char(string="Name", help="Name")
    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        ondelete="restrict",
        index=True,
    )  # FHIR Field: definition

    activity_definition_id = fields.Many2one(
        comodel_name="workflow.activity.definition",
        ondelete="restrict",
        index=True,
    )  # FHIR Field: definition

    plan_definition_action_id = fields.Many2one(
        comodel_name="workflow.plan.definition.action", index=True
    )  # FHIR Field: definition
    state = fields.Selection(
        selection=lambda r: r._get_states(),
        readonly=False,
        states={"completed": [("readonly", True)]},
        required=True,
        tracking=True,
        index=True,
        default="preparation",
    )  # FHIR field: status
    service_id = fields.Many2one(
        string="Service",
        comodel_name="product.product",
        ondelete="restrict",
        index=True,
        domain="[('type', '=', 'service')]",
    )  # FHIR Field: code
    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="medical.patient",
        required=True,
        tracking=True,
        ondelete="restrict",
        index=True,
        help="Patient Name",
    )  # FHIR field: subject
    occurrence_date = fields.Datetime(
        string="Occurrence date", help="Occurrence of the order."
    )  # FHIR Field: occurrence
    performer_id = fields.Many2one(
        string="Performer",
        comodel_name="res.partner",
        ondelete="restrict",
        index=True,
        tracking=True,
        domain=[("is_practitioner", "=", True)],
        help="Who is to perform the procedure",
    )  # FHIR Field : performer/actor
    is_editable = fields.Boolean(compute="_compute_is_editable")

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in (
                "suspended",
                "aborted",
                "completed",
                "entered-in-error",
                "unknown",
            ):
                rec.is_editable = False
            else:
                rec.is_editable = True

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    def preparation2in_progress_values(self):
        return {"state": "in-progress"}

    def preparation2in_progress(self):
        self.write(self.preparation2in_progress_values())

    def suspended2in_progress_values(self):
        return {"state": "in-progress"}

    def suspended2in_progress(self):
        self.write(self.suspended2in_progress_values())

    def in_progress2completed_values(self):
        return {"state": "completed"}

    def in_progress2completed(self):
        self.write(self.in_progress2completed_values())

    def in_progress2aborted_values(self):
        return {"state": "aborted"}

    def in_progress2aborted(self):
        self.write(self.in_progress2aborted_values())

    def in_progress2suspended_values(self):
        return {"state": "suspended"}

    def in_progress2suspended(self):
        self.write(self.in_progress2suspended_values())
