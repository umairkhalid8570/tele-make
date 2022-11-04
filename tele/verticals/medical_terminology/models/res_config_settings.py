
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_medical_terminology_atc = fields.Boolean("ATC terminology")
    module_medical_terminology_sct = fields.Boolean("SCT terminology")
