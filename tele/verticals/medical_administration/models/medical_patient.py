
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import api, fields, models


class MedicalPatient(models.Model):
    # FHIR Entity: Patient (http://hl7.org/fhir/patient.html)
    _name = "medical.patient"
    _description = "Medical Patient"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        "res.partner", required=True, ondelete="restrict"
    )

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")]
    )  # FHIR Field: gender
    # https://www.hl7.org/fhir/valueset-administrative-gender.html)
    marital_status = fields.Selection(
        [
            ("s", "Single"),
            ("m", "Married"),
            ("w", "Widowed"),
            ("d", "Divorced"),
            ("l", "Separated"),
        ]
    )  # FHIR Field: maritalStatus
    # https://www.hl7.org/fhir/valueset-marital-status.html
    birth_date = fields.Date(string="Birth date")  # FHIR Field: birthDate
    deceased_date = fields.Date(
        string="Deceased date"
    )  # FHIR Field: deceasedDate
    is_deceased = fields.Boolean(
        compute="_compute_is_deceased"
    )  # FHIR Field: deceasedBoolean

    @api.depends("deceased_date")
    def _compute_is_deceased(self):
        for record in self:
            record.is_deceased = bool(record.deceased_date)

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.patient") or "/"

    @api.model
    def create(self, vals):
        vals_upd = vals.copy()
        return super(MedicalPatient, self).create(vals_upd)

    def open_parent(self):
        """Utility method used to add an "Open Parent" button in partner
        views"""
        self.ensure_one()
        address_form_id = self.env.ref("base.view_partner_address_form").id
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "views": [(address_form_id, "form")],
            "res_id": self.parent_id.id,
            "target": "new",
            "flags": {"form": {"action_buttons": True}},
        }
