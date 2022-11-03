# -*- coding: utf-8 -*-

from tele import models, fields, api, _
from tele.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from tele.exceptions import ValidationError
import datetime
import json
from tele.applets.tele_dashboard_ninja.common_lib.tele_date_filter_selections import tele_get_date, tele_convert_into_local, \
    tele_convert_into_utc
from tele.tools.safe_eval import safe_eval
import locale
from dateutil.parser import parse


class TeleDashboardNinjaBoard(models.Model):
    _name = 'tele_dashboard_ninja.board'
    _description = 'Dashboard Ninja'

    name = fields.Char(string="Dashboard Name", required=True, size=35)
    tele_dashboard_items_ids = fields.One2many('tele_dashboard_ninja.item', 'tele_dashboard_ninja_board_id',
                                             string='Dashboard Items')
    tele_dashboard_menu_name = fields.Char(string="Menu Name")
    tele_dashboard_top_menu_id = fields.Many2one('ir.ui.menu',
                                               domain="['|',('action','=',False),('parent_id','=',False)]",
                                               string="Show Under Menu",
                                               default=lambda self: self.env['ir.ui.menu'].search(
                                                   [('name', '=', 'My Dashboard')]))
    tele_dashboard_client_action_id = fields.Many2one('ir.actions.client')
    tele_dashboard_menu_id = fields.Many2one('ir.ui.menu')
    tele_dashboard_state = fields.Char()
    tele_dashboard_active = fields.Boolean(string="Active", default=True)
    tele_dashboard_group_access = fields.Many2many('res.groups', string="Group Access")

    # DateFilter Fields
    tele_dashboard_start_date = fields.Datetime(string="Start Date")
    tele_dashboard_end_date = fields.Datetime(string="End Date")
    tele_date_filter_selection = fields.Selection([
        ('l_none', 'All Time'),
        ('l_day', 'Today'),
        ('t_week', 'This Week'),
        ('t_month', 'This Month'),
        ('t_quarter', 'This Quarter'),
        ('t_year', 'This Year'),
        ('n_day', 'Next Day'),
        ('n_week', 'Next Week'),
        ('n_month', 'Next Month'),
        ('n_quarter', 'Next Quarter'),
        ('n_year', 'Next Year'),
        ('ls_day', 'Last Day'),
        ('ls_week', 'Last Week'),
        ('ls_month', 'Last Month'),
        ('ls_quarter', 'Last Quarter'),
        ('ls_year', 'Last Year'),
        ('l_week', 'Last 7 days'),
        ('l_month', 'Last 30 days'),
        ('l_quarter', 'Last 90 days'),
        ('l_year', 'Last 365 days'),
        ('ls_past_until_now', 'Past Till Now'),
        ('ls_pastwithout_now', ' Past Excluding Today'),
        ('n_future_starting_now', 'Future Starting Now'),
        ('n_futurestarting_tomorrow', 'Future Starting Tomorrow'),
        ('l_custom', 'Custom Filter'),
    ], default='l_none', string="Default Date Filter")

    # for setting Global/Indian Format
    tele_data_formatting = fields.Selection([
        ('global', 'Global'),
        ('indian', 'Indian'),
        ('exact', 'Exact')
    ], string='Format')

    tele_gridstack_config = fields.Char('Item Configurations')
    tele_dashboard_default_template = fields.Many2one('tele_dashboard_ninja.board_template',
                                                    default=lambda self: self.env.ref('tele_dashboard_ninja.tele_blank',
                                                                                      False),
                                                    string="Dashboard Template")

    tele_set_interval = fields.Selection([
        ('15000', '15 Seconds'),
        ('30000', '30 Seconds'),
        ('45000', '45 Seconds'),
        ('60000', '1 minute'),
        ('120000', '2 minute'),
        ('300000', '5 minute'),
        ('600000', '10 minute'),
    ], string="Default Update Interval", help="Update Interval for new items only")
    tele_dashboard_menu_sequence = fields.Integer(string="Menu Sequence", default=10,
                                                help="Smallest sequence give high priority and Highest sequence give "
                                                     "low priority")
    tele_child_dashboard_ids = fields.One2many('tele_dashboard_ninja.child_board', 'tele_dashboard_ninja_id')
    tele_dashboard_defined_filters_ids = fields.One2many('tele_dashboard_ninja.board_defined_filters',
                                                       'tele_dashboard_board_id',
                                                       string='Dashboard Predefined Filters')
    tele_dashboard_custom_filters_ids = fields.One2many('tele_dashboard_ninja.board_custom_filters',
                                                      'tele_dashboard_board_id',
                                                      string='Dashboard Custom Filters')
    multi_layouts = fields.Boolean(string='Enable Multi-Dashboard Layouts',
                                   help='Allow user to have multiple layouts of the same Dashboard')


    @api.constrains('tele_dashboard_start_date', 'tele_dashboard_end_date')
    def tele_date_validation(self):
        for rec in self:
            if rec.tele_dashboard_start_date > rec.tele_dashboard_end_date:
                raise ValidationError(_('Start date must be less than end date'))

    @api.model
    def create(self, vals):
        record = super(TeleDashboardNinjaBoard, self).create(vals)
        if 'tele_dashboard_top_menu_id' in vals and 'tele_dashboard_menu_name' in vals:
            action_id = {
                'name': vals['tele_dashboard_menu_name'] + " Action",
                'res_model': 'tele_dashboard_ninja.board',
                'tag': 'tele_dashboard_ninja',
                'params': {'tele_dashboard_id': record.id},
            }
            record.tele_dashboard_client_action_id = self.env['ir.actions.client'].sudo().create(action_id)

            record.tele_dashboard_menu_id = self.env['ir.ui.menu'].sudo().create({
                'name': vals['tele_dashboard_menu_name'],
                'active': vals.get('tele_dashboard_active', True),
                'parent_id': vals['tele_dashboard_top_menu_id'],
                'action': "ir.actions.client," + str(record.tele_dashboard_client_action_id.id),
                'groups_id': vals.get('tele_dashboard_group_access', False),
                'sequence': vals.get('tele_dashboard_menu_sequence', 10)
            })

        if record.tele_dashboard_default_template and record.tele_dashboard_default_template.tele_item_count:
            tele_gridstack_config = {}
            template_data = json.loads(record.tele_dashboard_default_template.tele_gridstack_config)
            for item_data in template_data:
                if record.tele_dashboard_default_template.tele_template_type == 'tele_custom':
                    dashboard_item = self.env['tele_dashboard_ninja.item'].browse(int(item_data)).copy(
                        {'tele_dashboard_ninja_board_id': record.id})
                    tele_gridstack_config[dashboard_item.id] = template_data[item_data]
                else:
                    dashboard_item = self.env.ref(item_data['item_id']).copy({'tele_dashboard_ninja_board_id': record.id})
                    tele_gridstack_config[dashboard_item.id] = item_data['data']
            record.tele_gridstack_config = json.dumps(tele_gridstack_config)
        return record

    @api.onchange('tele_date_filter_selection')
    def tele_date_filter_selection_onchange(self):
        for rec in self:
            if rec.tele_date_filter_selection and rec.tele_date_filter_selection != 'l_custom':
                rec.tele_dashboard_start_date = False
                rec.tele_dashboard_end_date = False

    def write(self, vals):
        if vals.get('tele_date_filter_selection', False) and vals.get('tele_date_filter_selection') != 'l_custom':
            vals.update({
                'tele_dashboard_start_date': False,
                'tele_dashboard_end_date': False

            })
        record = super(TeleDashboardNinjaBoard, self).write(vals)
        for rec in self:
            if 'tele_dashboard_menu_name' in vals:
                if self.env.ref('tele_dashboard_ninja.tele_my_default_dashboard_board') and self.env.ref(
                        'tele_dashboard_ninja.tele_my_default_dashboard_board').sudo().id == rec.id:
                    if self.env.ref('tele_dashboard_ninja.board_menu_root', False):
                        self.env.ref('tele_dashboard_ninja.board_menu_root').sudo().name = vals['tele_dashboard_menu_name']
                else:
                    rec.tele_dashboard_menu_id.sudo().name = vals['tele_dashboard_menu_name']
            if 'tele_dashboard_group_access' in vals:
                if self.env.ref('tele_dashboard_ninja.tele_my_default_dashboard_board').id == rec.id:
                    if self.env.ref('tele_dashboard_ninja.board_menu_root', False):
                        self.env.ref('tele_dashboard_ninja.board_menu_root').groups_id = vals['tele_dashboard_group_access']
                else:
                    rec.tele_dashboard_menu_id.sudo().groups_id = vals['tele_dashboard_group_access']
            if 'tele_dashboard_active' in vals and rec.tele_dashboard_menu_id:
                rec.tele_dashboard_menu_id.sudo().active = vals['tele_dashboard_active']

            if 'tele_dashboard_top_menu_id' in vals:
                rec.tele_dashboard_menu_id.write(
                    {'parent_id': vals['tele_dashboard_top_menu_id']}
                )

            if 'tele_dashboard_menu_sequence' in vals:
                rec.tele_dashboard_menu_id.sudo().sequence = vals['tele_dashboard_menu_sequence']

        return record

    def unlink(self):
        if self.env.ref('tele_dashboard_ninja.tele_my_default_dashboard_board').id in self.ids:
            raise ValidationError(_("Default Dashboard can't be deleted."))
        else:
            for rec in self:
                rec.tele_dashboard_client_action_id.sudo().unlink()
                rec.tele_child_dashboard_ids.unlink()
                rec.tele_dashboard_menu_id.sudo().unlink()
                rec.tele_dashboard_items_ids.unlink()
        res = super(TeleDashboardNinjaBoard, self).unlink()
        return res

    def tele_get_grid_config(self):
        default_grid_id = self.env['tele_dashboard_ninja.child_board'].search(
            [['id', 'in', self.tele_child_dashboard_ids.ids], ['company_id', '=', self.env.company.id],
             ['board_type', '=', 'default']])

        if not default_grid_id:
            default_grid_id = self.env['tele_dashboard_ninja.child_board'].create({
                "tele_gridstack_config": self.tele_gridstack_config,
                "tele_dashboard_ninja_id": self.id,
                "name": "Default Board Layout",
                "company_id": self.env.company.id,
                "board_type": "default",
            })

        return default_grid_id

    @api.model
    def tele_fetch_dashboard_data(self, tele_dashboard_id, tele_item_domain=False):
        """
        Return Dictionary of Dashboard Data.
        :param tele_dashboard_id: Integer
        :param tele_item_domain: List[List]
        :return: dict
        """

        tele_dn_active_ids = []
        if self._context.get('tele_dn_active_ids'):
            tele_dn_active_ids = self._context.get('tele_dn_active_ids')

        tele_dn_active_ids.append(tele_dashboard_id)
        self = self.with_context(
            tele_dn_active_ids=tele_dn_active_ids,
        )

        has_group_tele_dashboard_manager = self.env.user.has_group('tele_dashboard_ninja.tele_dashboard_ninja_group_manager')
        tele_dashboard_rec = self.browse(tele_dashboard_id)
        dashboard_data = {
            'name': tele_dashboard_rec.name,
            'multi_layouts': tele_dashboard_rec.multi_layouts,
            'tele_company_id': self.env.company.id,
            'tele_dashboard_manager': has_group_tele_dashboard_manager,
            'tele_dashboard_list': self.search_read([], ['id', 'name']),
            'tele_dashboard_start_date': self._context.get('teleDateFilterStartDate', False) or self.browse(
                tele_dashboard_id).tele_dashboard_start_date,
            'tele_dashboard_end_date': self._context.get('teleDateFilterEndDate', False) or self.browse(
                tele_dashboard_id).tele_dashboard_end_date,
            'tele_date_filter_selection': self._context.get('teleDateFilterSelection', False) or self.browse(
                tele_dashboard_id).tele_date_filter_selection,
            'tele_gridstack_config': "{}",
            'tele_set_interval': tele_dashboard_rec.tele_set_interval,
            'tele_data_formatting': tele_dashboard_rec.tele_data_formatting,
            'tele_dashboard_items_ids': tele_dashboard_rec.tele_dashboard_items_ids.ids,
            'tele_item_data': {},
            'tele_child_boards': False,
            'tele_selected_board_id': False,
            'tele_dashboard_domain_data': tele_dashboard_rec.tele_prepare_dashboard_domain(),
            'tele_dashboard_pre_domain_filter': tele_dashboard_rec.tele_prepare_dashboard_pre_domain(),
            'tele_dashboard_custom_domain_filter': tele_dashboard_rec.tele_prepare_dashboard_custom_domain(),
            'tele_item_model_relation': dict([(x['id'], [x['tele_model_name'], x['tele_model_name_2']]) for x in
                                            tele_dashboard_rec.tele_dashboard_items_ids.read(
                                                ['tele_model_name', 'tele_model_name_2'])]),
            'tele_model_item_relation': {},
        }

        default_grid_id = tele_dashboard_rec.tele_get_grid_config()
        dashboard_data['tele_gridstack_config'] = default_grid_id.tele_gridstack_config
        dashboard_data['tele_gridstack_config_id'] = default_grid_id.id

        if self.env['tele_dashboard_ninja.child_board'].search(
                [['id', 'in', tele_dashboard_rec.tele_child_dashboard_ids.ids], ['company_id', '=', self.env.company.id],
                 ['board_type', '!=', 'default']], limit=1):
            dashboard_data['tele_child_boards'] = {
                'tele_default': [tele_dashboard_rec.name, default_grid_id.tele_gridstack_config]}
            selecred_rec = self.env['tele_dashboard_ninja.child_board'].search(
                [['id', 'in', tele_dashboard_rec.tele_child_dashboard_ids.ids], ['tele_active', '=', True],
                 ['company_id', '=', self.env.company.id], ['board_type', '!=', 'default']], limit=1)
            if selecred_rec:
                dashboard_data['tele_selected_board_id'] = str(selecred_rec.id)
                dashboard_data['tele_gridstack_config'] = selecred_rec.tele_gridstack_config
            else:
                dashboard_data['tele_selected_board_id'] = 'tele_default'
            for rec in self.env['tele_dashboard_ninja.child_board'].search_read(
                    [['id', 'in', tele_dashboard_rec.tele_child_dashboard_ids.ids],
                     ['company_id', '=', self.env.company.id], ['board_type', '!=', 'default']],
                    ['name', 'tele_gridstack_config']):
                dashboard_data['tele_child_boards'][str(rec['id'])] = [rec['name'], rec['tele_gridstack_config']]
        tele_item_domain = tele_item_domain or []
        try:
            items = self.tele_dashboard_items_ids.search(
                [['tele_dashboard_ninja_board_id', '=', tele_dashboard_id]] + tele_item_domain).ids
        except Exception as e:
            items = self.tele_dashboard_items_ids.search(
                [['tele_dashboard_ninja_board_id', '=', tele_dashboard_id]] + tele_item_domain).ids
        dashboard_data['tele_dashboard_items_ids'] = items
        return dashboard_data

    @api.model
    def tele_fetch_item(self, item_list, tele_dashboard_id, params={}):
        """
        :rtype: object
        :param item_list: list of item ids.
        :return: {'id':[item_data]}
        """
        self = self.tele_set_date(tele_dashboard_id)
        items = {}
        item_model = self.env['tele_dashboard_ninja.item']
        for item_id in item_list:
            item = self.tele_fetch_item_data(item_model.browse(item_id), params)
            items[item['id']] = item
        return items

    # fetching Item info (Divided to make function inherit easily)
    def tele_fetch_item_data(self, rec, params={}):
        """
        :rtype: object
        :param item_id: item object
        :return: object with formatted item data
        """
        try:
            tele_precision = self.sudo().env.ref('tele_dashboard_ninja.tele_dashboard_ninja_precision')
            tele_precision_digits = tele_precision.digits
            if tele_precision_digits < 0:
                tele_precision_digits = 2
            if tele_precision_digits > 100:
                tele_precision_digits = 2
        except Exception as e:
            tele_precision_digits = 2

        action = {}
        item_domain1 = params.get('tele_domain_1', [])
        item_domain2 = params.get('tele_domain_2', [])
        if rec.tele_actions:
            context = {}
            try:
                context = eval(rec.tele_actions.context)
            except Exception:
                context = {}

                # Managing those views that have the access rights
            tele_actions = rec.tele_actions.sudo()
            action['name'] = tele_actions.name
            action['type'] = tele_actions.type
            action['res_model'] = tele_actions.res_model
            action['views'] = tele_actions.views
            action['view_mode'] = tele_actions.view_mode
            action['search_view_id'] = tele_actions.search_view_id.id
            action['context'] = context
            action['target'] = 'current'
        elif rec.tele_is_client_action and rec.tele_client_action:
            clint_action = {}
            tele_client_action = rec.tele_client_action.sudo()
            clint_action['name'] = tele_client_action.name
            clint_action['type'] = tele_client_action.type
            clint_action['res_model'] = tele_client_action.res_model
            clint_action['xml_id'] = tele_client_action.xml_id
            clint_action['tag'] = tele_client_action.tag
            clint_action['binding_type'] = tele_client_action.binding_type
            clint_action['params'] = tele_client_action.params
            clint_action['target'] = 'current'

            action = clint_action,
        else:
            action = False
        tele_currency_symbol = False
        tele_currency_position = False
        if rec.tele_unit and rec.tele_unit_selection == 'monetary':
            try:
                tele_currency_symbol = self.env.user.company_id.currency_id.symbol
                tele_currency_position = self.env.user.company_id.currency_id.position
            except Exception as E:
                tele_currency_symbol = False
                tele_currency_position = False

        item = {
            'name': rec.name if rec.name else rec.tele_model_id.name if rec.tele_model_id else "Name",
            'tele_background_color': rec.tele_background_color,
            'tele_font_color': rec.tele_font_color,
            'tele_header_bg_color': rec.tele_header_bg_color,
            # 'tele_domain': rec.tele_domain.replace('"%UID"', str(
            #     self.env.user.id)) if rec.tele_domain and "%UID" in rec.tele_domain else rec.tele_domain,
            'tele_domain': rec.tele_convert_into_proper_domain(rec.tele_domain, rec, item_domain1),
            'tele_dashboard_id': rec.tele_dashboard_ninja_board_id.id,
            'tele_icon': rec.tele_icon,
            'tele_model_id': rec.tele_model_id.id,
            'tele_model_name': rec.tele_model_name,
            'tele_model_display_name': rec.tele_model_id.name,
            'tele_record_count_type': rec.tele_record_count_type,
            'tele_record_count': rec._teleGetRecordCount(item_domain1),
            'id': rec.id,
            'tele_layout': rec.tele_layout,
            'tele_icon_select': rec.tele_icon_select,
            'tele_default_icon': rec.tele_default_icon,
            'tele_default_icon_color': rec.tele_default_icon_color,
            # Pro Fields
            'tele_dashboard_item_type': rec.tele_dashboard_item_type,
            'tele_chart_item_color': rec.tele_chart_item_color,
            'tele_chart_groupby_type': rec.tele_chart_groupby_type,
            'tele_chart_relation_groupby': rec.tele_chart_relation_groupby.id,
            'tele_chart_relation_groupby_name': rec.tele_chart_relation_groupby.name,
            'tele_chart_date_groupby': rec.tele_chart_date_groupby,
            'tele_record_field': rec.tele_record_field.id if rec.tele_record_field else False,
            'tele_chart_data': rec._tele_get_chart_data(item_domain1),
            'tele_list_view_data': rec._teleGetListViewData(item_domain1),
            'tele_chart_data_count_type': rec.tele_chart_data_count_type,
            'tele_bar_chart_stacked': rec.tele_bar_chart_stacked,
            'tele_semi_circle_chart': rec.tele_semi_circle_chart,
            'tele_list_view_type': rec.tele_list_view_type,
            'tele_list_view_group_fields': rec.tele_list_view_group_fields.ids if rec.tele_list_view_group_fields else False,
            'tele_previous_period': rec.tele_previous_period,
            'tele_kpi_data': rec._teleGetKpiData(item_domain1, item_domain2),
            'tele_goal_enable': rec.tele_goal_enable,
            'tele_model_id_2': rec.tele_model_id_2.id,
            'tele_record_field_2': rec.tele_record_field_2.id,
            'tele_data_comparison': rec.tele_data_comparison,
            'tele_target_view': rec.tele_target_view,
            'tele_date_filter_selection': rec.tele_date_filter_selection,
            'tele_show_data_value': rec.tele_show_data_value,
            'tele_show_records': rec.tele_show_records,
            # 'action_id': rec.tele_actions.id if rec.tele_actions else False,
            'sequence': 0,
            'max_sequnce': len(rec.tele_action_lines) if rec.tele_action_lines else False,
            'action': action,
            'tele_hide_legend': rec.tele_hide_legend,
            'tele_data_calculation_type': rec.tele_data_calculation_type,
            'tele_export_all_records': rec.tele_export_all_records,
            'tele_data_formatting': rec.tele_data_format,
            'tele_is_client_action': rec.tele_is_client_action,
            'tele_pagination_limit': rec.tele_pagination_limit,
            'tele_record_data_limit': rec.tele_record_data_limit,
            'tele_chart_cumulative_field': rec.tele_chart_cumulative_field.ids,
            'tele_chart_cumulative': rec.tele_chart_cumulative,
            'tele_chart_is_cumulative': rec.tele_chart_is_cumulative,
            'tele_button_color': rec.tele_button_color,
            'tele_to_do_data': rec._teleGetToDOData(),
            'tele_multiplier_active': rec.tele_multiplier_active,
            'tele_multiplier': rec.tele_multiplier,
            'tele_goal_liness': True if rec.tele_goal_lines else False,
            'tele_currency_symbol': tele_currency_symbol,
            'tele_currency_position': tele_currency_position,
            'tele_precision_digits': tele_precision_digits if tele_precision_digits else 2,
            'tele_data_label_type': rec.tele_data_label_type
        }
        return item

    def tele_set_date(self, tele_dashboard_id):
        tele_dashboard_rec = self.browse(tele_dashboard_id)
        if self._context.get('teleDateFilterSelection', False):
            tele_date_filter_selection = self._context['teleDateFilterSelection']
            if tele_date_filter_selection == 'l_custom':
                tele_start_dt_parse = parse(self._context['teleDateFilterStartDate'])
                tele_end_dt_parse = parse(self._context['teleDateFilterEndDate'])
                self = self.with_context(
                    teleDateFilterStartDate=fields.datetime.strptime(tele_start_dt_parse.strftime("%Y-%m-%d %H:%M:%S"),
                                                                   "%Y-%m-%d %H:%M:%S"))
                self = self.with_context(
                    teleDateFilterEndDate=fields.datetime.strptime(tele_end_dt_parse.strftime("%Y-%m-%d %H:%M:%S"),
                                                                 "%Y-%m-%d %H:%M:%S"))
                self = self.with_context(teleIsDefultCustomDateFilter=False)

        else:
            tele_date_filter_selection = tele_dashboard_rec.tele_date_filter_selection
            self = self.with_context(teleDateFilterStartDate=tele_dashboard_rec.tele_dashboard_start_date)
            self = self.with_context(teleDateFilterEndDate=tele_dashboard_rec.tele_dashboard_end_date)
            self = self.with_context(teleDateFilterSelection=tele_date_filter_selection)
            self = self.with_context(teleIsDefultCustomDateFilter=True)

        if tele_date_filter_selection not in ['l_custom', 'l_none']:
            tele_date_data = tele_get_date(tele_date_filter_selection, self, 'datetime')
            self = self.with_context(teleDateFilterStartDate=tele_date_data["selected_start_date"])
            self = self.with_context(teleDateFilterEndDate=tele_date_data["selected_end_date"])

        return self

    @api.model
    def tele_get_list_view_data_offset(self, tele_dashboard_item_id, offset, dashboard_id, params={}):
        item_domain = params.get('tele_domain_1', [])
        self = self.tele_set_date(dashboard_id)
        item = self.tele_dashboard_items_ids.browse(tele_dashboard_item_id)

        return item.tele_get_next_offset(tele_dashboard_item_id, offset, item_domain)

    def tele_view_items_view(self):
        self.ensure_one()
        return {
            'name': _("Dashboard Items"),
            'res_model': 'tele_dashboard_ninja.item',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(False, 'tree'), (False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('tele_dashboard_ninja_board_id', '!=', False)],
            'search_view_id': self.env.ref('tele_dashboard_ninja.tele_item_search_view').id,
            'context': {
                'search_default_tele_dashboard_ninja_board_id': self.id,
                'group_by': 'tele_dashboard_ninja_board_id',
            },
            'help': _('''<p class="o_view_nocontent_smiling_face">
                                        You can find all items related to Dashboard Here.</p>
                                    '''),

        }

    def tele_export_item(self, item_id):
        return {
            'tele_file_format': 'tele_dashboard_ninja_item_export',
            'item': self.tele_export_item_data(self.tele_dashboard_items_ids.browse(int(item_id)))
        }

    # fetching Item info (Divided to make function inherit easily)
    def tele_export_item_data(self, rec):
        tele_timezone = self._context.get('tz') or self.env.user.tz
        tele_chart_measure_field = []
        tele_chart_measure_field_2 = []
        if rec.tele_many2many_field_ordering:
            tele_many2many_field_ordering = json.loads(rec.tele_many2many_field_ordering)
        else:
            tele_many2many_field_ordering =  {}
        if tele_many2many_field_ordering.get('tele_list_view_fields', False):
            tele_list_view_fields_list = self.env['ir.model.fields'].search([('id', 'in',
                                                    tele_many2many_field_ordering.get('tele_list_view_fields', False))])
        if tele_many2many_field_ordering.get('tele_list_view_group_fields', False):
            tele_list_view_group_fields_list = self.env['ir.model.fields'].search([('id', 'in',
                                           tele_many2many_field_ordering.get('tele_list_view_group_fields', False))])
        if tele_many2many_field_ordering.get('tele_chart_measure_field', False):
            tele_chart_measure_field_list = self.env['ir.model.fields'].search([('id', 'in',
                                   tele_many2many_field_ordering.get('tele_chart_measure_field', False))])
        if tele_many2many_field_ordering.get('tele_chart_measure_field_2', False):
            tele_chart_measure_field_2_list = self.env['ir.model.fields'].search([('id', 'in',
                               tele_many2many_field_ordering.get('tele_chart_measure_field_2', False))])

        try:
            for res in tele_chart_measure_field_list:
                tele_chart_measure_field.append(res.name)
        except Exception as E:
            tele_chart_measure_field = []
        try:
            for res in tele_chart_measure_field_2_list:
                tele_chart_measure_field_2.append(res.name)
        except Exception as E:
            tele_chart_measure_field_2 = []
        tele_multiplier_fields = []
        tele_multiplier_value = []
        if rec.tele_multiplier_lines:
            for ress in rec.tele_multiplier_lines.tele_multiplier_fields:
                tele_multiplier_fields.append(ress.name)
            for tele_val in rec.tele_multiplier_lines:
                tele_multiplier_value.append(tele_val.tele_multiplier_value)

        tele_list_view_group_fields = []
        try:
            for res in tele_list_view_group_fields_list:
                tele_list_view_group_fields.append(res.name)
        except Exception as e:
            tele_list_view_group_fields = []
        tele_goal_lines = []
        for res in rec.tele_goal_lines:
            goal_line = {
                'tele_goal_date': datetime.datetime.strftime(res.tele_goal_date, "%Y-%m-%d"),
                'tele_goal_value': res.tele_goal_value,
            }
            tele_goal_lines.append(goal_line)
        tele_dn_header_lines = []
        for res in rec.tele_dn_header_lines:
            tele_dn_header_line = {
                'tele_to_do_header': res.tele_to_do_header
            }

            if res.tele_to_do_description_lines:
                tele_to_do_description_lines = []
                for tele_description_line in res.tele_to_do_description_lines:
                    description_line = {
                        'tele_description': tele_description_line.tele_description,
                        'tele_active': tele_description_line.tele_active,
                    }
                    tele_to_do_description_lines.append(description_line)
                tele_dn_header_line[res.tele_to_do_header] = tele_to_do_description_lines
            tele_dn_header_lines.append(tele_dn_header_line)

        tele_action_lines = []
        for res in rec.tele_action_lines:
            action_line = {
                'tele_item_action_field': res.tele_item_action_field.name,
                'tele_item_action_date_groupby': res.tele_item_action_date_groupby,
                'tele_chart_type': res.tele_chart_type,
                'tele_sort_by_field': res.tele_sort_by_field.name,
                'tele_sort_by_order': res.tele_sort_by_order,
                'tele_record_limit': res.tele_record_limit,
                'sequence': res.sequence,
            }
            tele_action_lines.append(action_line)
        tele_multiplier_lines = []
        for res in rec.tele_multiplier_lines:
            tele_multiplier_line = {
                'tele_multiplier_fields': res.tele_multiplier_fields.id,
                'tele_multiplier_value': res.tele_multiplier_value,
                'tele_dashboard_item_id': rec.id,
                'tele_model_id': rec.tele_model_id.id
            }
            tele_multiplier_lines.append(tele_multiplier_line)

        tele_list_view_field = []
        try:
            for res in tele_list_view_fields_list:
                tele_list_view_field.append(res.name)
        except Exception as e:
            tele_list_view_field = []
        val = str(rec.id)
        selecred_rec = self.env['tele_dashboard_ninja.child_board'].search(
            [['id', 'in', rec.tele_dashboard_ninja_board_id.tele_child_dashboard_ids.ids], ['tele_active', '=', True],
             ['company_id', '=', self.env.company.id]], limit=1)
        if rec.tele_dashboard_ninja_board_id.tele_gridstack_config:
            keys_data = json.loads(rec.tele_dashboard_ninja_board_id.tele_gridstack_config)
        elif selecred_rec:
            keys_data = json.loads(selecred_rec.tele_gridstack_config)
        elif rec.tele_dashboard_ninja_board_id.tele_child_dashboard_ids[0].tele_gridstack_config:
            keys_data = json.loads(rec.tele_dashboard_ninja_board_id.tele_child_dashboard_ids[0].tele_gridstack_config)
        else:
            keys_data = {rec.id: json.loads(rec.grid_corners.replace("\'", "\""))}
        keys_list = keys_data.keys()
        grid_corners = {}
        if val in keys_list:
            grid_corners = keys_data.get(str(val))

        item = {
            'name': rec.name if rec.name else rec.tele_model_id.name if rec.tele_model_id else "Name",
            'tele_background_color': rec.tele_background_color,
            'tele_font_color': rec.tele_font_color,
            'tele_header_bg_color': rec.tele_header_bg_color,
            'tele_domain': rec.tele_domain,
            'tele_icon': str(rec.tele_icon) if rec.tele_icon else False,
            'tele_id': rec.id,
            'tele_model_id': rec.tele_model_name,
            'tele_record_count': rec.tele_record_count,
            'tele_layout': rec.tele_layout,
            'tele_icon_select': rec.tele_icon_select,
            'tele_default_icon': rec.tele_default_icon,
            'tele_default_icon_color': rec.tele_default_icon_color,
            'tele_record_count_type': rec.tele_record_count_type,
            # Pro Fields
            'tele_dashboard_item_type': rec.tele_dashboard_item_type,
            'tele_chart_item_color': rec.tele_chart_item_color,
            'tele_chart_groupby_type': rec.tele_chart_groupby_type,
            'tele_chart_relation_groupby': rec.tele_chart_relation_groupby.name,
            'tele_chart_date_groupby': rec.tele_chart_date_groupby,
            'tele_record_field': rec.tele_record_field.name,
            'tele_chart_sub_groupby_type': rec.tele_chart_sub_groupby_type,
            'tele_chart_relation_sub_groupby': rec.tele_chart_relation_sub_groupby.name,
            'tele_chart_date_sub_groupby': rec.tele_chart_date_sub_groupby,
            'tele_chart_data_count_type': rec.tele_chart_data_count_type,
            'tele_chart_measure_field': tele_chart_measure_field,
            'tele_chart_measure_field_2': tele_chart_measure_field_2,
            'tele_list_view_fields': tele_list_view_field,
            'tele_list_view_group_fields': tele_list_view_group_fields,
            'tele_list_view_type': rec.tele_list_view_type,
            'tele_record_data_limit': rec.tele_record_data_limit,
            'tele_sort_by_order': rec.tele_sort_by_order,
            'tele_sort_by_field': rec.tele_sort_by_field.name,
            'tele_date_filter_field': rec.tele_date_filter_field.name,
            'tele_goal_enable': rec.tele_goal_enable,
            'tele_standard_goal_value': rec.tele_standard_goal_value,
            'tele_goal_liness': tele_goal_lines,
            'tele_date_filter_selection': rec.tele_date_filter_selection,
            'tele_item_start_date': rec.tele_item_start_date.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if rec.tele_item_start_date else False,
            'tele_item_end_date': rec.tele_item_end_date.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if rec.tele_item_end_date else False,
            'tele_date_filter_selection_2': rec.tele_date_filter_selection_2,
            'tele_item_start_date_2': rec.tele_item_start_date_2.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if rec.tele_item_start_date_2 else False,
            'tele_item_end_date_2': rec.tele_item_end_date_2.strftime(
                DEFAULT_SERVER_DATETIME_FORMAT) if rec.tele_item_end_date_2 else False,
            'tele_previous_period': rec.tele_previous_period,
            'tele_target_view': rec.tele_target_view,
            'tele_data_comparison': rec.tele_data_comparison,
            'tele_record_count_type_2': rec.tele_record_count_type_2,
            'tele_record_field_2': rec.tele_record_field_2.name,
            'tele_model_id_2': rec.tele_model_id_2.model,
            'tele_date_filter_field_2': rec.tele_date_filter_field_2.name,
            'tele_action_liness': tele_action_lines,
            'tele_compare_period': rec.tele_compare_period,
            'tele_year_period': rec.tele_year_period,
            'tele_compare_period_2': rec.tele_compare_period_2,
            'tele_year_period_2': rec.tele_year_period_2,
            'tele_domain_2': rec.tele_domain_2,
            'tele_show_data_value': rec.tele_show_data_value,
            'tele_list_target_deviation_field': rec.tele_list_target_deviation_field.name,
            'tele_unit': rec.tele_unit,
            'tele_show_records': rec.tele_show_records,
            'tele_hide_legend': rec.tele_hide_legend,
            'tele_fill_temporal': rec.tele_fill_temporal,
            'tele_domain_extension': rec.tele_domain_extension,
            'tele_unit_selection': rec.tele_unit_selection,
            'tele_chart_unit': rec.tele_chart_unit,
            'tele_bar_chart_stacked': rec.tele_bar_chart_stacked,
            'tele_goal_bar_line': rec.tele_goal_bar_line,
            'tele_actions': rec.tele_actions.xml_id if rec.tele_actions else False,
            'tele_client_action': rec.tele_client_action.xml_id if rec.tele_client_action else False,
            'tele_is_client_action': rec.tele_is_client_action,
            'tele_export_all_records': rec.tele_export_all_records,
            'tele_record_data_limit_visibility': rec.tele_record_data_limit_visibility,
            'tele_data_format': rec.tele_data_format,
            'tele_pagination_limit': rec.tele_pagination_limit,
            'tele_chart_cumulative_field': rec.tele_chart_cumulative_field.ids,
            'tele_chart_cumulative': rec.tele_chart_cumulative,
            'tele_button_color': rec.tele_button_color,
            'tele_dn_header_line': tele_dn_header_lines,
            'tele_semi_circle_chart': rec.tele_semi_circle_chart,
            'tele_multiplier_active': rec.tele_multiplier_active,
            'tele_multiplier': rec.tele_multiplier,
            'tele_multiplier_lines': tele_multiplier_lines if tele_multiplier_lines else False,
            'tele_many2many_field_ordering': rec.tele_many2many_field_ordering,
        }
        if grid_corners:
            item.update({
                'grid_corners': grid_corners,
            })
        return item

    def tele_open_import(self, **kwargs):
        action = self.env['ir.actions.act_window']._for_xml_id('tele_dashboard_ninja.tele_import_dashboard_action')
        return action

    def tele_open_setting(self, **kwargs):
        action = self.env['ir.actions.act_window']._for_xml_id('tele_dashboard_ninja.board_form_tree_action_window')
        action['res_id'] = self.id
        action['target'] = 'new'
        action['context'] = {'create': False}
        return action

    def tele_delete_dashboard(self):
        if str(self.id) in self.tele_dashboard_default_template:
            raise ValidationError(_('You cannot delete any default template'))
        else:
            self.search([('id', '=', self.id)]).unlink()
            return {
                'type': 'ir.actions.client',
                'name': "Dashboard Ninja",
                'res_model': 'tele_deshboard_ninja.board',
                'params': {'tele_dashboard_id': 1},
                'tag': 'tele_dashboard_ninja',
            }

    def tele_create_dashboard(self):
        action = self.env['ir.actions.act_window']._for_xml_id('tele_dashboard_ninja.board_form_tree_action_window')
        action['target'] = 'new'
        return action

    def tele_import_item(self, dashboard_id, **kwargs):
        try:
            # tele_dashboard_data = json.loads(file)
            file = kwargs.get('file', False)
            tele_dashboard_file_read = json.loads(file)
        except Exception:
            raise ValidationError(_("This file is not supported"))

        if 'tele_file_format' in tele_dashboard_file_read and tele_dashboard_file_read[
            'tele_file_format'] == 'tele_dashboard_ninja_item_export':
            item = tele_dashboard_file_read['item']
        else:
            raise ValidationError(_("Current Json File is not properly formatted according to Dashboard Ninja Model."))

        item['tele_dashboard_ninja_board_id'] = int(dashboard_id)
        item['tele_company_id'] = False
        self.tele_create_item(item)

        return "Success"

    @api.model
    def tele_dashboard_export(self, tele_dashboard_ids, **kwargs):
        tele_dashboard_data = []
        tele_dashboard_export_data = {}
        if kwargs.get('dashboard_id'):
            tele_dashboard_ids = '['+str(tele_dashboard_ids)+']'
        tele_dashboard_ids = json.loads(tele_dashboard_ids)
        for tele_dashboard_id in tele_dashboard_ids:
            dash = self.search([('id', '=', tele_dashboard_id)])
            selecred_rec = self.env['tele_dashboard_ninja.child_board'].search(
                [['id', 'in', dash.tele_child_dashboard_ids.ids], ['tele_active', '=', True],
                 ['company_id', '=', self.env.company.id]], limit=1)
            tele_dashboard_rec = self.browse(tele_dashboard_id)
            if selecred_rec:
                name = selecred_rec.name
                grid_conf = selecred_rec.tele_gridstack_config
            elif dash.tele_child_dashboard_ids:
                name = dash.display_name
                grid_conf = dash.tele_child_dashboard_ids[0].tele_gridstack_config
            else:
                name = dash.name
                grid_conf = dash.tele_gridstack_config
            dashboard_data = self.tele_prepare_export_data_vals(tele_dashboard_rec, grid_conf=grid_conf)
            if selecred_rec:
                dashboard_data['name'] = selecred_rec.name
                dashboard_data['tele_gridstack_config'] = selecred_rec.tele_gridstack_config
            elif len(tele_dashboard_rec.tele_child_dashboard_ids) > 1:
                dashboard_data['name'] = tele_dashboard_rec.tele_child_dashboard_ids[0].name
                dashboard_data['tele_gridstack_config'] = tele_dashboard_rec.tele_child_dashboard_ids[0].tele_gridstack_config
            if dashboard_data['name'] == 'Default Board Layout':
                dashboard_data['name'] = tele_dashboard_rec.tele_dashboard_menu_name
            if len(tele_dashboard_rec.tele_dashboard_items_ids) < 1:
                dashboard_data['tele_item_data'] = False
            else:
                items = []
                for rec in tele_dashboard_rec.tele_dashboard_items_ids:
                    item = self.tele_export_item_data(rec)
                    items.append(item)

                dashboard_data['tele_item_data'] = items
            tele_dashboard_data.append(dashboard_data)

            tele_dashboard_export_data = {
                'tele_file_format': 'tele_dashboard_ninja_export_file',
                'tele_dashboard_data': tele_dashboard_data
            }
        return tele_dashboard_export_data

    def tele_prepare_export_data_vals(self, tele_dashboard_rec, grid_conf=None,):
        dashboard_data = {
            'name': tele_dashboard_rec.name,
            'tele_dashboard_menu_name': tele_dashboard_rec.tele_dashboard_menu_name,
            'tele_gridstack_config': grid_conf if grid_conf else '{}',
            'tele_set_interval': tele_dashboard_rec.tele_set_interval,
            'tele_date_filter_selection': tele_dashboard_rec.tele_date_filter_selection,
            'tele_dashboard_start_date': tele_dashboard_rec.tele_dashboard_start_date,
            'tele_dashboard_end_date': tele_dashboard_rec.tele_dashboard_end_date,
            'tele_dashboard_top_menu_id': tele_dashboard_rec.tele_dashboard_top_menu_id.id,
            'tele_data_formatting': tele_dashboard_rec.tele_data_formatting,
        }
        return dashboard_data

    @api.model
    def tele_import_dashboard(self, file, menu_id):
        try:
            # tele_dashboard_data = json.loads(file)
            tele_dashboard_file_read = json.loads(file)
        except Exception:
            raise ValidationError(_("This file is not supported"))

        if 'tele_file_format' in tele_dashboard_file_read and tele_dashboard_file_read[
            'tele_file_format'] == 'tele_dashboard_ninja_export_file':
            tele_dashboard_data = tele_dashboard_file_read['tele_dashboard_data']
        else:
            raise ValidationError(_("Current Json File is not properly formatted according to Dashboard Ninja Model."))

        tele_dashboard_key = ['name', 'tele_dashboard_menu_name', 'tele_gridstack_config']
        tele_dashboard_item_key = ['tele_model_id', 'tele_chart_measure_field', 'tele_list_view_fields', 'tele_record_field',
                                 'tele_chart_relation_groupby', 'tele_id']

        # Fetching dashboard model info
        for data in tele_dashboard_data:
            if not all(key in data for key in tele_dashboard_key):
                raise ValidationError(
                    _("Current Json File is not properly formatted according to Dashboard Ninja Model."))
            tele_dashboard_top_menu_id = data.get('tele_dashboard_top_menu_id', False)
            if tele_dashboard_top_menu_id:
                try:
                    self.env['ir.ui.menu'].browse(tele_dashboard_top_menu_id).name
                    tele_dashboard_top_menu_id = self.env['ir.ui.menu'].browse(tele_dashboard_top_menu_id)
                except Exception:
                    tele_dashboard_top_menu_id = False
            vals = self.tele_prepare_import_data_vals(data, menu_id)
            # Creating Dashboard
            dashboard_id = self.create(vals)

            if data['tele_gridstack_config']:
                tele_gridstack_config = eval(data['tele_gridstack_config'])
            tele_grid_stack_config = {}

            item_ids = []
            item_new_ids = []
            tele_skiped = False
            if data['tele_item_data']:
                # Fetching dashboard item info
                tele_skiped = 0
                for item in data['tele_item_data']:
                    item['tele_company_id'] = False
                    if not all(key in item for key in tele_dashboard_item_key):
                        raise ValidationError(
                            _("Current Json File is not properly formatted according to Dashboard Ninja Model."))

                    # Creating dashboard items
                    item['tele_dashboard_ninja_board_id'] = dashboard_id.id
                    item_ids.append(item['tele_id'])
                    del item['tele_id']

                    if 'tele_data_calculation_type' in item:
                        if item['tele_data_calculation_type'] == 'custom':
                            del item['tele_data_calculation_type']
                            del item['tele_custom_query']
                            del item['tele_xlabels']
                            del item['tele_ylabels']
                            del item['tele_list_view_layout']
                            tele_item = self.tele_create_item(item)
                            item_new_ids.append(tele_item.id)
                        else:
                            tele_skiped += 1
                    else:
                        tele_item = self.tele_create_item(item)
                        item_new_ids.append(tele_item.id)

            for id_index, id in enumerate(item_ids):
                if data['tele_gridstack_config'] and str(id) in tele_gridstack_config:
                    tele_grid_stack_config[str(item_new_ids[id_index])] = tele_gridstack_config[str(id)]
                    # if id_index in item_new_ids:

            self.browse(dashboard_id.id).write({
                'tele_gridstack_config': json.dumps(tele_grid_stack_config)
            })

            if tele_skiped:
                return {
                    'tele_skiped_items': tele_skiped,
                }

        return "Success"
        # separate function to make item for import

    def tele_prepare_import_data_vals(self, data, menu_id):
        vals = {
            'name': data['name'],
            'tele_dashboard_menu_name': data['tele_dashboard_menu_name'],
            'tele_dashboard_top_menu_id': menu_id.id if menu_id else self.env.ref(
                "tele_dashboard_ninja.board_menu_root").id,
            'tele_dashboard_active': True,
            'tele_gridstack_config': data['tele_gridstack_config'],
            'tele_dashboard_default_template': self.env.ref("tele_dashboard_ninja.tele_blank").id,
            'tele_dashboard_group_access': False,
            'tele_set_interval': data['tele_set_interval'],
            'tele_date_filter_selection': data['tele_date_filter_selection'],
            'tele_dashboard_start_date': data['tele_dashboard_start_date'],
            'tele_dashboard_end_date': data['tele_dashboard_end_date'],
        }
        return vals

    def tele_create_item(self, item):
        model = self.env['ir.model'].search([('model', '=', item['tele_model_id'])])

        if not model and not item['tele_dashboard_item_type'] == 'tele_to_do':
            raise ValidationError(_(
                "Please Install the Module which contains the following Model : %s " % item['tele_model_id']))

        tele_model_name = item['tele_model_id']

        tele_goal_lines = item['tele_goal_liness'].copy() if item.get('tele_goal_liness', False) else False
        tele_action_lines = item['tele_action_liness'].copy() if item.get('tele_action_liness', False) else False
        tele_multiplier_lines = item['tele_multiplier_lines'].copy() if item.get('tele_multiplier_lines', False) else False
        tele_dn_header_line = item['tele_dn_header_line'].copy() if item.get('tele_dn_header_line', False) else False

        # Creating dashboard items
        item = self.tele_prepare_item(item)

        if 'tele_goal_liness' in item:
            del item['tele_goal_liness']
        if 'tele_id' in item:
            del item['tele_id']
        if 'tele_action_liness' in item:
            del item['tele_action_liness']
        if 'tele_icon' in item:
            item['tele_icon_select'] = "Default"
            item['tele_icon'] = False
        if 'tele_dn_header_line' in item:
            del item['tele_dn_header_line']
        if 'tele_multiplier_lines' in item:
            del item['tele_multiplier_lines']

        tele_item = self.env['tele_dashboard_ninja.item'].create(item)

        if tele_goal_lines and len(tele_goal_lines) != 0:
            for line in tele_goal_lines:
                line['tele_goal_date'] = datetime.datetime.strptime(line['tele_goal_date'].split(" ")[0],
                                                                  '%Y-%m-%d')
                line['tele_dashboard_item'] = tele_item.id
                self.env['tele_dashboard_ninja.item_goal'].create(line)

        if tele_dn_header_line and len(tele_dn_header_line) != 0:
            for line in tele_dn_header_line:
                tele_line = {}
                tele_line['tele_to_do_header'] = line.get('tele_to_do_header')
                tele_line['tele_dn_item_id'] = tele_item.id
                tele_dn_header_id = self.env['tele_to.do.headers'].create(tele_line)
                if line.get(line.get('tele_to_do_header'), False):
                    for tele_task in line.get(line.get('tele_to_do_header')):
                        tele_task['tele_to_do_header_id'] = tele_dn_header_id.id
                        self.env['tele_to.do.description'].create(tele_task)

        if tele_action_lines and len(tele_action_lines) != 0:

            for line in tele_action_lines:
                if line['tele_sort_by_field']:
                    tele_sort_by_field = line['tele_sort_by_field']
                    tele_sort_record_id = self.env['ir.model.fields'].search(
                        [('model', '=', tele_model_name), ('name', '=', tele_sort_by_field)])
                    if tele_sort_record_id:
                        line['tele_sort_by_field'] = tele_sort_record_id.id
                    else:
                        line['tele_sort_by_field'] = False
                if line['tele_item_action_field']:
                    tele_item_action_field = line['tele_item_action_field']
                    tele_record_id = self.env['ir.model.fields'].search(
                        [('model', '=', tele_model_name), ('name', '=', tele_item_action_field)])
                    if tele_record_id:
                        line['tele_item_action_field'] = tele_record_id.id
                        line['tele_dashboard_item_id'] = tele_item.id
                        self.env['tele_dashboard_ninja.item_action'].create(line)

        if tele_multiplier_lines and len(tele_multiplier_lines) != 0:
            for rec in tele_multiplier_lines:
                tele_multiplier_field = rec['tele_multiplier_fields']
                tele_multiplier_field_id = self.env['ir.model.fields'].search(
                    [('model', '=', tele_model_name), ('id', '=', tele_multiplier_field)])
                if tele_multiplier_field:
                    rec['tele_multiplier_fields'] = tele_multiplier_field_id.id
                    rec['tele_dashboard_item_id'] = tele_item.id
                    self.env['tele_dashboard_item.multiplier'].create(rec)

        return tele_item

    def tele_prepare_item(self, item):
        tele_measure_field_ids = []
        tele_measure_field_2_ids = []
        tele_many2many_field_ordering = item['tele_many2many_field_ordering']
        tele_list_view_group_fields_name = False
        tele_list_view_fields_name = False
        tele_chart_measure_field_name = False
        tele_chart_measure_field_2_name = False
        if tele_many2many_field_ordering:
            tele_many2many_field_ordering = json.loads(tele_many2many_field_ordering)
            tele_list_view_group_fields_name = tele_many2many_field_ordering.get('tele_list_view_group_fields_name', False)
            tele_list_view_fields_name = tele_many2many_field_ordering.get('tele_list_view_fields_name', False)
            tele_chart_measure_field_name = tele_many2many_field_ordering.get('tele_chart_measure_field_name', False)
            tele_chart_measure_field_2_name = tele_many2many_field_ordering.get('tele_chart_measure_field_2_name', False)
        tele_chart_measure_field = item['tele_chart_measure_field']
        if tele_chart_measure_field_name and len(tele_chart_measure_field_name)>0:
            tele_chart_measure_field = tele_chart_measure_field_name
        for tele_measure in tele_chart_measure_field:
            tele_measure_id = self.env['ir.model.fields'].search(
                [('name', '=', tele_measure), ('model', '=', item['tele_model_id'])])
            if tele_measure_id:
                tele_measure_field_ids.append(tele_measure_id.id)
        item['tele_chart_measure_field'] = [(6, 0, tele_measure_field_ids)]
        tele_chart_measure_field_2 = item['tele_chart_measure_field_2']
        if tele_chart_measure_field_name and len(tele_chart_measure_field_name) > 0:
            tele_chart_measure_field_2 = tele_chart_measure_field_2_name
        for tele_measure in tele_chart_measure_field_2:
            tele_measure_id = self.env['ir.model.fields'].search(
                [('name', '=', tele_measure), ('model', '=', item['tele_model_id'])])
            if tele_measure_id:
                tele_measure_field_2_ids.append(tele_measure_id.id)
        item['tele_chart_measure_field_2'] = [(6, 0, tele_measure_field_2_ids)]

        tele_list_view_group_fields_ids = []
        tele_list_view_group_fields = item['tele_list_view_group_fields']
        if tele_list_view_group_fields_name and len(tele_list_view_group_fields_name) > 0:
            tele_list_view_group_fields = tele_list_view_group_fields_name
        for tele_measure in tele_list_view_group_fields:
            tele_measure_id = self.env['ir.model.fields'].search(
                [('name', '=', tele_measure), ('model', '=', item['tele_model_id'])])

            if tele_measure_id:
                tele_list_view_group_fields_ids.append(tele_measure_id.id)
        item['tele_list_view_group_fields'] = [(6, 0, tele_list_view_group_fields_ids)]

        tele_list_view_field_ids = []

        tele_list_view_fields = item['tele_list_view_fields']
        if tele_list_view_fields_name and len(tele_list_view_fields_name) > 0:
            tele_list_view_fields = tele_list_view_group_fields_name
        for tele_list_field in tele_list_view_fields:
            tele_list_field_id = self.env['ir.model.fields'].search(
                [('name', '=', tele_list_field), ('model', '=', item['tele_model_id'])])
            if tele_list_field_id:
                tele_list_view_field_ids.append(tele_list_field_id.id)
        item['tele_list_view_fields'] = [(6, 0, tele_list_view_field_ids)]

        if item['tele_record_field']:
            tele_record_field = item['tele_record_field']
            tele_record_id = self.env['ir.model.fields'].search(
                [('name', '=', tele_record_field), ('model', '=', item['tele_model_id'])])
            if tele_record_id:
                item['tele_record_field'] = tele_record_id.id
            else:
                item['tele_record_field'] = False

        if item['tele_date_filter_field']:
            tele_date_filter_field = item['tele_date_filter_field']
            tele_record_id = self.env['ir.model.fields'].search(
                [('name', '=', tele_date_filter_field), ('model', '=', item['tele_model_id'])])
            if tele_record_id:
                item['tele_date_filter_field'] = tele_record_id.id
            else:
                item['tele_date_filter_field'] = False

        if item['tele_chart_relation_groupby']:
            tele_group_by = item['tele_chart_relation_groupby']
            tele_record_id = self.env['ir.model.fields'].search(
                [('name', '=', tele_group_by), ('model', '=', item['tele_model_id'])])
            if tele_record_id:
                item['tele_chart_relation_groupby'] = tele_record_id.id
            else:
                item['tele_chart_relation_groupby'] = False

        if item['tele_chart_relation_sub_groupby']:
            tele_group_by = item['tele_chart_relation_sub_groupby']
            tele_chart_relation_sub_groupby = self.env['ir.model.fields'].search(
                [('name', '=', tele_group_by), ('model', '=', item['tele_model_id'])])
            if tele_chart_relation_sub_groupby:
                item['tele_chart_relation_sub_groupby'] = tele_chart_relation_sub_groupby.id
            else:
                item['tele_chart_relation_sub_groupby'] = False

        # Sort by field : Many2one Entery
        if item['tele_sort_by_field']:
            tele_group_by = item['tele_sort_by_field']
            tele_sort_by_field = self.env['ir.model.fields'].search(
                [('name', '=', tele_group_by), ('model', '=', item['tele_model_id'])])
            if tele_sort_by_field:
                item['tele_sort_by_field'] = tele_sort_by_field.id
            else:
                item['tele_sort_by_field'] = False

        if item['tele_list_target_deviation_field']:
            tele_list_target_deviation_field = item['tele_list_target_deviation_field']
            record_id = self.env['ir.model.fields'].search(
                [('name', '=', tele_list_target_deviation_field), ('model', '=', item['tele_model_id'])])
            if record_id:
                item['tele_list_target_deviation_field'] = record_id.id
            else:
                item['tele_list_target_deviation_field'] = False

        tele_model_id = self.env['ir.model'].search([('model', '=', item['tele_model_id'])]).id

        if item.get("tele_actions"):
            tele_action = self.env.ref(item["tele_actions"], False)
            if tele_action:
                item["tele_actions"] = tele_action.id
            else:
                item["tele_actions"] = False
        if item.get("tele_client_action"):
            tele_action = self.env.ref(item["tele_client_action"], False)
            if tele_action:
                item["tele_client_action"] = tele_action.id
            else:
                item["tele_client_action"] = False

        if (item['tele_model_id_2']):
            tele_model_2 = item['tele_model_id_2'].replace(".", "_")
            tele_model_id_2 = self.env['ir.model'].search([('model', '=', item['tele_model_id_2'])]).id
            if item['tele_record_field_2']:
                tele_record_field = item['tele_record_field_2']
                tele_record_id = self.env['ir.model.fields'].search(
                    [('model', '=', item['tele_model_id_2']), ('name', '=', tele_record_field)])

                if tele_record_id:
                    item['tele_record_field_2'] = tele_record_id.id
                else:
                    item['tele_record_field_2'] = False
            if item['tele_date_filter_field_2']:
                tele_record_id = self.env['ir.model.fields'].search(
                    [('model', '=', item['tele_model_id_2']), ('name', '=', item['tele_date_filter_field_2'])])

                if tele_record_id:
                    item['tele_date_filter_field_2'] = tele_record_id.id
                else:
                    item['tele_date_filter_field_2'] = False

            item['tele_model_id_2'] = tele_model_id_2
        else:
            item['tele_date_filter_field_2'] = False
            item['tele_record_field_2'] = False

        item['tele_model_id'] = tele_model_id

        item['tele_goal_liness'] = False
        item['tele_item_start_date'] = item['tele_item_start_date'] if \
            item['tele_item_start_date'] else False
        item['tele_item_end_date'] = item['tele_item_end_date'] if \
            item['tele_item_end_date'] else False
        item['tele_item_start_date_2'] = item['tele_item_start_date_2'] if \
            item['tele_item_start_date_2'] else False
        item['tele_item_end_date_2'] = item['tele_item_end_date_2'] if \
            item['tele_item_end_date_2'] else False

        return item

    @api.model
    def update_child_board(self, action, dashboard_id, data):
        dashboard_id = self.browse(dashboard_id)
        selecred_rec = self.env['tele_dashboard_ninja.child_board'].search(
            [['id', 'in', dashboard_id.tele_child_dashboard_ids.ids],
             ['company_id', '=', self.env.company.id], ['tele_active', '=', True]], limit=1)
        if action == 'create':
            dashboard_id.tele_child_dashboard_ids.write({'tele_active': False})
            result = self.env['tele_dashboard_ninja.child_board'].create(data)
            result = result.id
        elif action == 'update':
            # result = dashboard_id.tele_child_dashboard_ids.search([['tele_active', '=', True]]).write({'tele_active': False})
            if data['tele_selected_board_id'] != 'tele_default':
                selecred_rec.tele_active = False
                result = dashboard_id.tele_child_dashboard_ids.browse(int(data['tele_selected_board_id'])).write(
                    {'tele_active': True})
            else:
                result = dashboard_id.tele_child_dashboard_ids.search([['tele_active', '=', True]]).write(
                    {'tele_active': False})
                for i in dashboard_id.tele_child_dashboard_ids:
                    if i.name == 'Default Board Layout':
                        i.tele_active = True
        return result

    def tele_prepare_dashboard_domain(self):
        pre_defined_filter_ids = self.env['tele_dashboard_ninja.board_defined_filters'].search(
            [['id', 'in', self.tele_dashboard_defined_filters_ids.ids], '|', ['tele_is_active', '=', True],
             ['display_type', '=', 'line_section']], order='sequence')
        data = {}
        filter_model_ids = pre_defined_filter_ids.mapped('tele_model_id').ids
        for model_id in filter_model_ids:
            filter_ids = self.env['tele_dashboard_ninja.board_defined_filters'].search(
                [['id', 'in', pre_defined_filter_ids.ids], '|', ['tele_model_id', '=', model_id],
                 ['display_type', '=', 'line_section']],
                order='sequence')
            connect_symbol = '|'
            for rec in filter_ids:
                if rec.display_type == 'line_section':
                    connect_symbol = '&'

                if data.get(rec.tele_model_id.model) and rec.tele_domain:
                    data[rec.tele_model_id.model]['domain'] = data[rec.tele_model_id.model]['domain'] + safe_eval(
                        rec.tele_domain)
                    data[rec.tele_model_id.model]['domain'].insert(0, connect_symbol)
                elif rec.tele_model_id.model:
                    tele_domain = rec.tele_domain
                    if tele_domain and "%UID" in tele_domain:
                        tele_domain = tele_domain.replace('"%UID"', str(self.env.user.id))
                    if tele_domain and "%MYCOMPANY" in tele_domain:
                        tele_domain = tele_domain.replace('"%MYCOMPANY"', str(self.env.company.id))
                    data[rec.tele_model_id.model] = {
                        'domain': safe_eval(tele_domain) if tele_domain else [],
                        'tele_domain_index_data': [],
                        'model_name': rec.tele_model_id.name,
                        'item_ids': self.env['tele_dashboard_ninja.item'].search(
                            [['id', 'in', self.tele_dashboard_items_ids.ids], '|',
                             ['tele_model_id', '=', rec.tele_model_id.id], ['tele_model_id_2', '=', rec.tele_model_id.id]]).ids
                    }

        return data

    def tele_prepare_dashboard_pre_domain(self):
        data = {}
        pre_defined_filter_ids = self.env['tele_dashboard_ninja.board_defined_filters'].search(
            [['id', 'in', self.tele_dashboard_defined_filters_ids.ids]], order='sequence')
        categ_seq = 1
        for rec in pre_defined_filter_ids:
            if rec.display_type == 'line_section':
                categ_seq = categ_seq + 1
            tele_domain = rec.tele_domain
            if tele_domain and "%UID" in tele_domain:
                tele_domain = tele_domain.replace('"%UID"', str(self.env.user.id))
            if tele_domain and "%MYCOMPANY" in tele_domain:
                tele_domain = tele_domain.replace('"%MYCOMPANY"', str(self.env.company.id))

            data[rec['id']] = {
                'id': rec.id,
                'name': rec.name,
                'model': rec.tele_model_id.model,
                'model_name': rec.tele_model_id.name,
                'active': rec.tele_is_active,
                'categ': rec.tele_model_id.model + '_' + str(categ_seq) if rec.display_type != 'line_section' else 0,
                'type': 'filter' if rec.display_type != 'line_section' else 'separator',
                'domain': safe_eval(tele_domain) if tele_domain else [],
                'sequence': rec.sequence
            }
        return data

    def tele_prepare_dashboard_custom_domain(self):
        custom_filter_ids = self.env['tele_dashboard_ninja.board_custom_filters'].search(
            [['id', 'in', self.tele_dashboard_custom_filters_ids.ids]], order='name')
        data = {}
        for rec in custom_filter_ids:
            data[str(rec.id)] = {
                'id': rec.id,
                'name': rec.name,
                'model': rec.tele_model_id.model,
                'model_name': rec.tele_model_id.name,
                'field_name': rec.tele_domain_field_id.name,
                'field_type': rec.tele_domain_field_id.ttype,
                'special_data': {}
            }
            if rec.tele_domain_field_id.ttype == 'selection':
                data[str(rec.id)]['special_data'] = {
                    'select_options':
                        self.env[rec.tele_model_id.model].fields_get(allfields=[rec.tele_domain_field_id.name])[
                            rec.tele_domain_field_id.name]['selection']
                }
        return data
