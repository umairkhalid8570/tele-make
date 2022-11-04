
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_medical_clinical_procedure = fields.Boolean("Procedures")
    module_medical_clinical_careplan = fields.Boolean("Care plans")
    module_medical_clinical_request_group = fields.Boolean("Request groups")
    module_medical_clinical_condition = fields.Boolean("Medical Condition")
