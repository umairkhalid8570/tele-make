# -*- coding: utf-8 -*-

from tele import models, fields, api, _
from tele.exceptions import UserError, ValidationError


class TeleDashboardEditorBoardItemAction(models.TransientModel):
    _name = 'tele_editor_dashboard.item_action'
    _description = 'Dashboard Editor Item Actions'

    name = fields.Char()
    tele_dashboard_item_ids = fields.Many2many("tele_dashboard_editor.item", string="Dashboard Items")
    tele_action = fields.Selection([('move', 'Move'),
                                  ('duplicate', 'Duplicate'),
                                  ], string="Action")
    tele_dashboard_editor_id = fields.Many2one("tele_dashboard_editor.board", string="Select Dashboard")
    tele_dashboard_editor_ids = fields.Many2many("tele_dashboard_editor.board", string="Select Dashboards")

    # Move or Copy item to another dashboard action

    def action_item_move_copy_action(self):
        if self.tele_action == 'move':
            for item in self.tele_dashboard_item_ids:
                item.tele_dashboard_editor_board_id = self.tele_dashboard_editor_id
        elif self.tele_action == 'duplicate':
            # Using sudo here to allow creating same item without any security error
            for dashboard_id in self.tele_dashboard_editor_ids:
                for item in self.tele_dashboard_item_ids:
                    item.sudo().copy({'tele_dashboard_editor_board_id': dashboard_id.id})
