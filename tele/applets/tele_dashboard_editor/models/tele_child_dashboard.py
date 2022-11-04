from tele import models, fields, api, _


class TeleDashboardEditorBoardItemAction(models.Model):
    _name = 'tele_dashboard_editor.child_board'
    _description = 'Dashboard Editor Child Board'

    name = fields.Char()
    tele_dashboard_editor_id = fields.Many2one("tele_dashboard_editor.board", string="Select Dashboard")
    tele_gridstack_config = fields.Char('Item Configurations')
    # tele_board_active_user_ids = fields.Many2many('res.users')
    tele_active = fields.Boolean("Is Selected")
    tele_dashboard_menu_name = fields.Char(string="Menu Name", related='tele_dashboard_editor_id.tele_dashboard_menu_name', store=True)
    board_type = fields.Selection([('default', 'Default'), ('child', 'Child')])
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

