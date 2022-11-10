# -*- coding: utf-8 -*-

from tele import api, fields, models


class TeleCreateDashboardWizard(models.TransientModel):
    _name = 'tele.dashboard.wizard'
    _description = 'Dashboard Creation Wizard'

    name = fields.Char(string="Dashboard Name", required=True)
    tele_menu_name = fields.Char(string="Menu Name", required=True)
    tele_top_menu_id = fields.Many2one('ir.ui.menu',
                                     domain="[('parent_id','=',False)]",
                                     string="Show Under Menu", required=True,
                                     default=lambda self: self.env['ir.ui.menu'].search(
                                         [('name', '=', 'My Dashboard')])[0])
    tele_sequence = fields.Integer(string="Sequence")
    tele_template = fields.Many2one('tele_dashboard_builder.board_template',
                                  default=lambda self: self.env.ref('tele_dashboard_builder.tele_blank',
                                                                    False),
                                  string="Dashboard Template")

    context = {}

    def CreateDashBoard(self):
        '''this function returns acion id of tele.dashboard.wizard'''
        action = self.env['ir.actions.act_window']._for_xml_id(
            'tele_dashboard_builder.tele_create_dashboard_wizard')
        return action

    def tele_create_record(self):
        '''this function creats record of tele_dashboard_builder.board and return dashboard action_id'''
        tele_create_record = self.env['tele_dashboard_builder.board'].create({
            'name': self.name,
            'tele_dashboard_menu_name': self.tele_menu_name,
            'tele_dashboard_menu_sequence': self.tele_sequence,
            'tele_dashboard_default_template': self.tele_template.id,
            'tele_dashboard_top_menu_id': self.tele_top_menu_id.id,
        })
        context = {'tele_reload_menu': True, 'tele_menu_id': tele_create_record.tele_dashboard_menu_id.id}
        return {
            'type': 'ir.actions.client',
            'name': "Dashboard Builder",
            'res_model': 'tele_dashboard_builder.board',
            'params': {'tele_dashboard_id': tele_create_record.id},
            'tag': 'tele_dashboard_builder',
            'context': self.with_context(context)._context
        }
