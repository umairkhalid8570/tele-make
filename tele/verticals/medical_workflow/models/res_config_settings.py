
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_patient_add_plan_definition = fields.Boolean(
        string="Add Plan Definition on patients",
        implied_group="medical_workflow." "group_patient_add_plan_definition",
    )

    group_main_activity_plan_definition = fields.Boolean(
        string="Allows to add a main activity definition on a Plan Definition",
        implied_group="medical_workflow."
        "group_main_activity_plan_definition",
    )
