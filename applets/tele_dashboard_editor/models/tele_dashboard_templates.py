from tele import models, fields, api, _


class TeleDashboardEditorTemplate(models.Model):
    _name = 'tele_dashboard_editor.board_template'
    _description = 'Dashboard Editor Template'

    name = fields.Char()
    tele_gridstack_config = fields.Char()
    tele_item_count = fields.Integer()
    tele_template_type = fields.Selection([('tele_default', 'Predefined'), ('tele_custom', 'Custom')],
                                        string="Template Format")
    tele_dashboard_item_ids = fields.One2many('tele_dashboard_editor.item', 'tele_dashboard_board_template_id',
                                            string="Template Type")
    tele_dashboard_board_id = fields.Many2one('tele_dashboard_editor.board', string="Dashboard", help="""
        Items Configuration and their position in the dashboard will be copied from the selected dashboard 
        and will be saved as template.
    """)

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('tele_template_type', False) and val.get('tele_dashboard_board_id', False):
                dashboard_id = self.env['tele_dashboard_editor.board'].browse(val.get('tele_dashboard_board_id'))
                val['tele_gridstack_config'] = dashboard_id.tele_gridstack_config
                val['tele_item_count'] = len(dashboard_id.tele_dashboard_items_ids)
                val['tele_dashboard_item_ids'] = [(4, x.copy({'tele_dashboard_editor_board_id': False}).id) for x in
                                                dashboard_id.tele_dashboard_items_ids]
        recs = super(TeleDashboardEditorTemplate, self).create(vals_list)
        return recs

    def write(self, val):
        if val.get('tele_dashboard_board_id', False):
            dashboard_id = self.env['tele_dashboard_editor.board'].browse(val.get('tele_dashboard_board_id'))
            val['tele_gridstack_config'] = dashboard_id.tele_gridstack_config
            val['tele_item_count'] = len(dashboard_id.tele_dashboard_items_ids)
            val['tele_dashboard_item_ids'] = [(6, 0,
                                             [x.copy({'tele_dashboard_editor_board_id': False}).id for x in
                                              dashboard_id.tele_dashboard_items_ids])]
        recs = super(TeleDashboardEditorTemplate, self).write(val)
        return recs
