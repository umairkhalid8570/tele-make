# -*- coding: utf-8 -*-

from tele import api, fields, models


class TeleCreateDashboardWizard(models.TransientModel):
    _name = 'tele.dashboard.duplicate.wizard'
    _description = 'Dashboard Duplicate Wizard'

    tele_top_menu_id = fields.Many2one('ir.ui.menu', string="Show Under Menu", required=True, domain="[('parent_id','=',False)]",
                                     default=lambda self: self.env['ir.ui.menu'].search(
                                         [('name', '=', 'My Dashboard')]))

    def DuplicateDashBoard(self):
        '''this function returns acion id of tele.dashboard.duplicate.wizard'''
        action = self.env['ir.actions.act_window']._for_xml_id(
            'tele_dashboard_ninja.tele_duplicate_dashboard_wizard')
        action['context'] = {'dashboard_id': self.id}
        return action

    def tele_duplicate_record(self):
        '''this function creats record of tele_dashboard_ninja.board and return dashboard action_id'''
        dashboard_id = self._context.get('dashboard_id')
        dup_dash = self.env['tele_dashboard_ninja.board'].browse(dashboard_id).copy({'tele_dashboard_top_menu_id': self.tele_top_menu_id.id})
        context = {'tele_reload_menu': True, 'tele_menu_id': dup_dash.tele_dashboard_menu_id.id}
        dash_id = self.env['tele_dashboard_ninja.board'].browse(dashboard_id)
        if not dup_dash.tele_dashboard_items_ids:
            for item in dash_id.tele_dashboard_items_ids:
                item.sudo().copy({'tele_dashboard_ninja_board_id': dup_dash.id})
        return {
            'type': 'ir.actions.client',
            'name': "Dashboard Ninja",
            'res_model': 'tele_deshboard_ninja.board',
            'params': {'tele_dashboard_id': dup_dash.id},
            'tag': 'tele_dashboard_ninja',
            'context': self.with_context(context)._context
        }


class TeleDeleteDashboardWizard(models.TransientModel):
    _name = 'tele.dashboard.delete.wizard'
    _description = 'Dashboard Delete Wizard'


    def DeleteDashBoard(self):
        '''this function returns acion id of tele.dashboard.duplicate.wizard'''
        action = self.env['ir.actions.act_window']._for_xml_id(
            'tele_dashboard_ninja.tele_delete_dashboard_wizard')
        action['context'] = {'dashboard_id': self.id}
        return action

    def tele_delete_record(self):
        '''this function creats record of tele_dashboard_ninja.board and return dashboard action_id'''
        dashboard_id = self._context.get('dashboard_id')
        self.env['tele_dashboard_ninja.board'].browse(dashboard_id).unlink()
        context = {'tele_reload_menu': True, 'tele_menu_id': self.env['ir.ui.menu'].search([('name', '=', 'My Dashboard')])[0].id}
        return {
            'type': 'ir.actions.client',
            'name': "Dashboard Ninja",
            'res_model': 'tele_deshboard_ninja.board',
            'params': {'tele_dashboard_id': 1},
            'tag': 'tele_dashboard_ninja',
            'context': self.with_context(context)._context
        }

