
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import api, fields, models


class MedicalSCTConcept(models.Model):
    _inherit = "medical.sct.concept"

    is_specialty = fields.Boolean(
        store=True, index=True, compute="_compute_is_specialty"
    )

    @api.depends("parent_ids")
    def _compute_is_specialty(self):
        for record in self:
            record.is_specialty = record.check_property(
                "is_specialty", ["394658006"]
            )
