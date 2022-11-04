
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import api, fields, models


class MedicalAllergySubstance(models.Model):

    _name = "medical.allergy.substance"
    _inherit = "medical.abstract"
    _description = "Substance/Pharmaceutical/Biological product codes"

    name = fields.Char(required=True)
    description = fields.Char()
    sct_code_id = fields.Many2one(
        comodel_name="medical.sct.concept",
        domain=[
            "|",
            ("is_clinical_substance", "=", True),
            ("is_pharmaceutical_product", "=", True),
        ],
    )
    create_warning = fields.Boolean(
        help="Mark if this allergy substance needs to create "
        "a warning for taking medical decisions"
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.allergy.substance")
            or "/"
        )
