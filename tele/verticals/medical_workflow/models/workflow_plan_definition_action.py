
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from tele import _, api, fields, models
from tele.exceptions import ValidationError

from .base_result import combine_result


class PlanDefinitionAction(models.Model):
    # FHIR entity: Action
    _name = "workflow.plan.definition.action"
    _description = "Medical Plan Definition Action"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = "name"
    _rec_name = "complete_name"

    name = fields.Char(
        string="Action name", required=True
    )  # FHIR field: title
    complete_name = fields.Char(
        "Full Action Name", compute="_compute_complete_name", store=True
    )
    parent_id = fields.Many2one(
        string="Parent Action",
        comodel_name="workflow.plan.definition.action",
        ondelete="cascade",
        domain="[('plan_definition_id', '=', plan_definition_id)]",
    )
    child_ids = fields.One2many(
        string="Child Actions",
        comodel_name="workflow.plan.definition.action",
        inverse_name="parent_id",
        required=True,
    )  # FHIR field: Action (sub-action)
    direct_plan_definition_id = fields.Many2one(
        string="Root Plan Definition",
        comodel_name="workflow.plan.definition",
        ondelete="cascade",
    )
    type_id = fields.Many2one(
        "workflow.type", related="plan_definition_id.type_id"
    )
    plan_definition_id = fields.Many2one(
        string="Plan Definition",
        comodel_name="workflow.plan.definition",
        compute="_compute_plan_definition_id",
        ondelete="cascade",
        store=True,
    )
    execute_plan_definition_id = fields.Many2one(
        string="Plan Definition to execute",
        comodel_name="workflow.plan.definition",
        ondelete="restrict",
        index=True,
        help="This plan will be executed instead of an activity",
    )
    activity_definition_id = fields.Many2one(
        string="Activity definition",
        comodel_name="workflow.activity.definition",
        ondelete="restrict",
        index=True,
    )  # FHIR field: definition (Activity Definition)
    parent_path = fields.Char(index=True)

    @api.depends("name", "parent_id")
    def _compute_complete_name(self):
        """Forms complete name of action from parent to child action."""
        for rec in self:
            name = rec.name
            current = rec
            while current.parent_id:
                current = current.parent_id
                name = "{}/{}".format(current.name, name)
            rec.complete_name = name

    @api.depends("parent_id", "direct_plan_definition_id")
    def _compute_plan_definition_id(self):
        for rec in self:
            rec.plan_definition_id = rec.direct_plan_definition_id
            if rec.parent_id:
                rec.plan_definition_id = rec.parent_id.plan_definition_id

    @api.onchange("plan_definition_id")
    def _onchange_plan_definition_id(self):
        return {
            "domain": {
                "activity_definition_id": [
                    (
                        "type_id",
                        "in",
                        [self.plan_definition_id.type_id.id, False],
                    )
                ]
            }
        }

    @api.onchange("activity_definition_id")
    def _onchange_activity_definition_id(self):
        self.name = self.activity_definition_id.name
        self.execute_plan_definition_id = False

    @api.onchange("execute_plan_definition_id")
    def _onchange_execute_plan_definition_id(self):
        self.name = self.execute_plan_definition_id.name
        self.activity_definition_id = False

    @api.constrains("execute_plan_definition_id", "child_ids")
    def _check_execute_plan_definition_id(self):
        for record in self:
            if record.execute_plan_definition_id:
                plan_ids = [record.plan_definition_id.id]
                self.execute_plan_definition_id._check_plan_recursion(plan_ids)
                if record.child_ids:
                    raise ValidationError(
                        _("Actions with Plans cannot have child actions")
                    )

    @api.constrains("execute_plan_definition_id", "activity_definition_id")
    def _check_execute_plan_activity_definition(self):
        for record in self:
            if (
                not record.execute_plan_definition_id
                and not record.activity_definition_id
            ):
                raise ValidationError(
                    _(
                        "Activity definition or Plan Definition must be defined "
                        "on each action"
                    )
                )

    def execute_action(self, vals, parent=False):
        self.ensure_one()
        if self.execute_plan_definition_id:
            return self.execute_plan_definition_id._execute_plan_definition(
                vals, parent
            )
        res = self.activity_definition_id.execute_activity(
            vals, parent, self.plan_definition_id, self
        )
        result = {res._name: res.ids}
        for action in self.child_ids:
            child_res, child_result = action.execute_action(vals, parent=res)
            result = combine_result(result, child_result)
        return res, result

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if "direct_action_ids" not in default:
            default["child_ids"] = [
                (0, 0, line.copy_data()[0]) for line in self.child_ids
            ]
        return super().copy_data(default)
