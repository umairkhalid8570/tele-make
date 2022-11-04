
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_medical_administration_practitioner_specialty = fields.Boolean(
        "Practitioner Specialty"
    )
