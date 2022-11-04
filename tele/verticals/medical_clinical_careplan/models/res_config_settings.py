
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_medical_careplan_add_plan_definition = fields.Boolean(
        string="Add Plan Definition on careplans",
        implied_group="medical_clinical_careplan."
        "group_medical_careplan_add_plan_definition",
    )
