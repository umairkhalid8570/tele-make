
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_medical_clinical = fields.Boolean("Clinical")
    module_medical_workflow = fields.Boolean("Workflow")
    module_medical_administration = fields.Boolean("Administration")
    module_medical_financial = fields.Boolean("Financial")
    module_medical_medication = fields.Boolean("Medication")
    module_medical_diagnostics = fields.Boolean("Diagnostics")
    module_medical_terminology = fields.Boolean("Terminologies")
