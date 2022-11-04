# -*- coding: utf-8 -*-
import dateutil
import datetime as dt
import pytz
import json
import babel
from datetime import timedelta
from tele.tools.safe_eval import safe_eval
from tele.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from collections import defaultdict
from datetime import datetime
from dateutil import relativedelta
from tele import models, fields, api, _
from tele.exceptions import ValidationError, UserError
from tele.applets.tele_dashboard_ninja.common_lib.tele_date_filter_selections import tele_get_date, tele_convert_into_utc, \
    tele_convert_into_local

# TODO : Check all imports if needed


read = fields.Many2one.read



def tele_read(self, records):
    if self.name == 'tele_list_view_fields' or self.name == 'tele_list_view_group_fields' or \
            self.name == 'tele_chart_measure_field' or self.name == 'tele_chart_measure_field_2':
        comodel = records.env[self.comodel_name]

        # String domains are supposed to be dynamic and evaluated on client-side
        # only (thus ignored here).
        domain = self.domain if isinstance(self.domain, list) else []

        wquery = comodel._where_calc(domain)
        comodel._apply_ir_rules(wquery, 'read')
        from_c, where_c, where_params = wquery.get_sql()
        query = """ SELECT {rel}.{id1}, {rel}.{id2} FROM {rel}, {from_c}
                    WHERE {where_c} AND {rel}.{id1} IN %s AND {rel}.{id2} = {tbl}.id
                """.format(rel=self.relation, id1=self.column1, id2=self.column2,
                           tbl=comodel._table, from_c=from_c, where_c=where_c or '1=1',
                           limit=(' LIMIT %d' % self.limit) if self.limit else '',
                           )
        where_params.append(tuple(records.ids))

        # retrieve lines and group them by record
        group = defaultdict(list)
        records._cr.execute(query, where_params)

        for record in records:
            if self.name == 'tele_list_view_fields':
                field = 'tele_list_view_fields'
            elif self.name == 'tele_chart_measure_field':
                field = 'tele_chart_measure_field'
            elif self.name == 'tele_chart_measure_field_2':
                field = 'tele_chart_measure_field_2'
            else:
                field = 'tele_list_view_group_fields'
            order = False
            if record.tele_many2many_field_ordering:
                order = json.loads(record.tele_many2many_field_ordering).get(field, False)


        rec_list = records._cr.fetchall()
        if order:
            for row in order:
                group[record.id].append(row)

        else:
            for row in rec_list:
                group[row[0]].append(row[1])

        # store result in cache
        cache = records.env.cache
        if order:
            try:
                group[record.id].sort(key=lambda x: order.index(x))
            except Exception as e:
                pass
        cache.set(record, self, tuple(group[record.id]))


    else:
        context = {'active_test': False}
        context.update(self.context)
        comodel = records.env[self.comodel_name].with_context(**context)
        domain = self.get_domain_list(records)
        comodel._flush_search(domain)
        wquery = comodel._where_calc(domain)
        comodel._apply_ir_rules(wquery, 'read')
        order_by = comodel._generate_order_by(None, wquery)
        from_c, where_c, where_params = wquery.get_sql()
        query = """ SELECT {rel}.{id1}, {rel}.{id2} FROM {rel}, {from_c}
                            WHERE {where_c} AND {rel}.{id1} IN %s AND {rel}.{id2} = {tbl}.id
                            {order_by} {limit} OFFSET {offset}
                        """.format(rel=self.relation, id1=self.column1, id2=self.column2,
                                   tbl=comodel._table, from_c=from_c, where_c=where_c or '1=1',
                                   limit=(' LIMIT %d' % self.limit) if self.limit else '',
                                   offset=0, order_by=order_by)
        where_params.append(tuple(records.ids))

        # retrieve lines and group them by record
        group = defaultdict(list)
        records._cr.execute(query, where_params)
        for row in records._cr.fetchall():
            group[row[0]].append(row[1])

        # store result in cache
        cache = records.env.cache
        for record in records:
            cache.set(record, self, tuple(group[record.id]))



fields.Many2many.read = tele_read

read_group = models.BaseModel._read_group_process_groupby


def tele_time_addition(self, gb, query):
    """
        Overwriting default to add minutes to Helper method to collect important
        information about groupbys: raw field name, type, time information, qualified name, ...
    """
    split = gb.split(':')
    field = self._fields.get(split[0])
    if not field:
        raise ValueError("Invalid field %r on model %r" % (split[0], self._name))
    field_type = field.type
    gb_function = split[1] if len(split) == 2 else None
    if gb_function == 'month_year':
        gb_function = 'month'
    temporal = field_type in ('date', 'datetime')
    tz_convert = field_type == 'datetime' and self._context.get('tz') in pytz.all_timezones
    qualified_field = self._inherits_join_calc(self._table, split[0], query)
    if temporal:
        lang = self.env['res.lang']._lang_get(self.env.user.lang).time_format
        if '%H' in lang:
            display_formats = {
                'minute': 'HH:mm dd MMM',
                'hour': 'HH:00 dd MMM',
                'day': 'dd MMM yyyy',  # yyyy = normal year
                'week': "'W'w YYYY",  # w YYYY = ISO week-year
                'month': 'MMMM yyyy',
                'quarter': 'QQQ yyyy',
                'year': 'yyyy',
            }
        else:
            display_formats = {
                'minute': 'hh:mm dd MMM',
                'hour': 'hh:00 dd MMM',
                'day': 'dd MMM yyyy',  # yyyy = normal year
                'week': "'W'w YYYY",  # w YYYY = ISO week-year
                'month': 'MMMM yyyy',
                'quarter': 'QQQ yyyy',
                'year': 'yyyy',
            }
        time_intervals = {
            'minute': dateutil.relativedelta.relativedelta(minutes=1),
            'hour': dateutil.relativedelta.relativedelta(hours=1),
            'day': dateutil.relativedelta.relativedelta(days=1),
            'week': dt.timedelta(days=7),
            'month': dateutil.relativedelta.relativedelta(months=1),
            'quarter': dateutil.relativedelta.relativedelta(months=3),
            'year': dateutil.relativedelta.relativedelta(years=1)
        }
        if tz_convert:
            qualified_field = "timezone('%s', timezone('UTC',%s))" % (self._context.get('tz', 'UTC'), qualified_field)
        qualified_field = "date_trunc('%s', %s::timestamp)" % (gb_function or 'month', qualified_field)
    if field_type == 'boolean':
        qualified_field = "coalesce(%s,false)" % qualified_field
    return {
        'field': split[0],
        'groupby': gb,
        'type': field_type,
        'display_format': display_formats[gb_function or 'month'] if temporal else None,
        'interval': time_intervals[gb_function or 'month'] if temporal else None,
        'tz_convert': tz_convert,
        'qualified_field': qualified_field,
        'granularity': gb_function or 'month' if temporal else None,
    }


models.BaseModel._read_group_process_groupby = tele_time_addition


class TeleDashboardNinjaItems(models.Model):
    _name = 'tele_dashboard_ninja.item'
    _description = 'Dashboard Ninja items'

    name = fields.Char(string="Name", size=256, help="The item will be represented by this unique name.")
    tele_model_id = fields.Many2one('ir.model', string='Model',
                                  domain="[('access_ids','!=',False),('transient','=',False),"
                                         "('model','not ilike','base_import%'),('model','not ilike','ir.%'),"
                                         "('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),"
                                         "('model','!=','mail.thread'),('model','not ilike','tele_dash%'),('model','not ilike','tele_to%')]",
                                  help="Data source to fetch and read the data for the creation of dashboard items. ")
    tele_dashboard_board_template_id = fields.Many2one('tele_dashboard_ninja.board_template', string="Dashboard Template")
    tele_domain = fields.Char(string="Domain", help="Define conditions for filter. ")

    tele_model_id_2 = fields.Many2one('ir.model', string='Kpi Model',
                                    domain="[('access_ids','!=',False),('transient','=',False),"
                                           "('model','not ilike','base_import%'),('model','not ilike','ir.%'),"
                                           "('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),"
                                           "('model','!=','mail.thread'),('model','not ilike','tele_dash%'), ('model','not ilike','tele_to%')]")

    tele_model_name_2 = fields.Char(related='tele_model_id_2.model', string="Kpi Model Name")

    # This field main purpose is to store %UID as current user id. Mainly used in JS file as container.
    tele_domain_temp = fields.Char(string="Domain Substitute")
    grid_corners = fields.Char(string="grid corners")
    tele_background_color = fields.Char(string="Background Color",
                                      default="#ffffff,0.99", help=' Select the background color with transparency. ')
    tele_icon = fields.Binary(string="Upload Icon", attachment=True)
    tele_default_icon = fields.Char(string="Icon", default="bar-chart", help='Select the icon to be displayed. ')
    tele_default_icon_color = fields.Char(default="#ffffff,0.99", string="Icon Color",
                                        help='Select the icon to be displayed. ')
    tele_icon_select = fields.Char(string="Icon Option", default="Default", help='Choose the Icon option. ')
    tele_font_color = fields.Char(default="#ffffff,0.99", string="Font Color", help='Select the font color. ')
    tele_dashboard_item_theme = fields.Char(string="Theme", default="white",
                                          help='Select the color theme for the display. ')
    tele_layout = fields.Selection([('layout1', 'Layout 1'),
                                  ('layout2', 'Layout 2'),
                                  ('layout3', 'Layout 3'),
                                  ('layout4', 'Layout 4'),
                                  ('layout5', 'Layout 5'),
                                  ('layout6', 'Layout 6'),
                                  ], default=('layout1'), required=True, string="Layout",
                                 help=' Select the layout to display records. ')
    tele_preview = fields.Integer(default=1, string="Preview")
    tele_model_name = fields.Char(related='tele_model_id.model', string="Model Name")

    tele_record_count_type_2 = fields.Selection([('count', 'Count'),
                                               ('sum', 'Sum'),
                                               ('average', 'Average')], string="Kpi Record Type", default="sum")
    tele_record_field_2 = fields.Many2one('ir.model.fields',
                                        domain="[('model_id','=',tele_model_id_2),('name','!=','id'),('name','!=','sequence'),('store','=',True),"
                                               "'|','|',('ttype','=','integer'),('ttype','=','float'),"
                                               "('ttype','=','monetary')]",
                                        string="Kpi Record Field")
    tele_record_count_2 = fields.Float(string="KPI Record Count", readonly=True, compute='tele_get_record_count_2',
                                     compute_sudo=False)
    tele_record_count_type = fields.Selection([('count', 'Count'),
                                             ('sum', 'Sum'),
                                             ('average', 'Average')], string="Record Type", default="count",
                                            help="Type of record how record will show as count,sum and average of the record")
    tele_record_count = fields.Float(string="Record Count", compute='tele_get_record_count', readonly=True,
                                   compute_sudo=False)
    tele_record_field = fields.Many2one('ir.model.fields',
                                      domain="[('model_id','=',tele_model_id),('name','!=','id'),('store','=',True),'|',"
                                             "'|',('ttype','=','integer'),('ttype','=','float'),"
                                             "('ttype','=','monetary')]",
                                      string="Record Field")
    tele_record_data_limit_visibility = fields.Boolean(string="Record Limit Data Visibility",
                                                     help="To enable the record data limit field")

    # Date Filter Fields
    # Condition to tell if date filter is applied or not
    tele_isDateFilterApplied = fields.Boolean(default=False)

    # ---------------------------- Date Filter Fields ------------------------------------------
    tele_date_filter_selection = fields.Selection([
        ('l_none', 'None'),
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
    ], string="Date Filter Selection", default="l_none", required=True,
        help='Select interval of the records to be displayed. ')
    tele_date_filter_field = fields.Many2one('ir.model.fields',
                                           domain="[('model_id','=',tele_model_id),('store','=',True),'|',('ttype','=','date'),"
                                                  "('ttype','=','datetime')]",
                                           string="Date Filter Field",
                                           help='Select the field for which Date Filter should be applicable.')

    tele_item_start_date = fields.Datetime(string="Start Date")
    tele_item_end_date = fields.Datetime(string="End Date")

    tele_date_filter_field_2 = fields.Many2one('ir.model.fields',
                                             domain="[('model_id','=',tele_model_id_2),('store','=',True),'|',('ttype','=','date'),"
                                                    "('ttype','=','datetime')]",
                                             string="Kpi Date Filter Field")

    tele_item_start_date_2 = fields.Datetime(string="Kpi Start Date")
    tele_item_end_date_2 = fields.Datetime(string="Kpi End Date")

    tele_domain_2 = fields.Char(string="Kpi Domain")
    tele_domain_2_temp = fields.Char(string="Kpi Domain Substitute")

    tele_date_filter_selection_2 = fields.Selection([
        ('l_none', "None"),
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
    ], string="Kpi Date Filter Selection", required=True, default='l_none')

    tele_previous_period = fields.Boolean(string=" Compare With Previous Period ", help='Checkbox to show comparison between the data of present day and the previous selected period. ')

    # ------------------------ Pro Fields --------------------
    tele_dashboard_ninja_board_id = fields.Many2one('tele_dashboard_ninja.board', string="Dashboard",
                                                  default=lambda self: self._context[
                                                      'tele_dashboard_id'] if 'tele_dashboard_id' in self._context
                                                  else False)

    # Chart related fields
    tele_dashboard_item_type = fields.Selection([('tele_tile', 'Tile'),
                                               ('tele_bar_chart', 'Bar Chart'),
                                               ('tele_horizontalBar_chart', 'Horizontal Bar Chart'),
                                               ('tele_line_chart', 'Line Chart'),
                                               ('tele_area_chart', 'Area Chart'),
                                               ('tele_pie_chart', 'Pie Chart'),
                                               ('tele_doughnut_chart', 'Doughnut Chart'),
                                               ('tele_polarArea_chart', 'Polar Area Chart'),
                                               ('tele_list_view', 'List View'),
                                               ('tele_kpi', 'KPI'),
                                               ('tele_to_do', 'To Do')
                                               ], default=lambda self: self._context.get('tele_dashboard_item_type',
                                                                                         'tele_tile'), required=True,
                                              string="Dashboard Item Type",
                                              help="Select the required type of dashboard to display. ")
    tele_chart_groupby_type = fields.Char(compute='get_chart_groupby_type', compute_sudo=False)
    tele_chart_sub_groupby_type = fields.Char(compute='get_chart_sub_groupby_type', compute_sudo=False)
    tele_chart_relation_groupby = fields.Many2one('ir.model.fields',
                                                domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),"
                                                       "('store','=',True),('ttype','!=','binary'),"
                                                       "('ttype','!=','many2many'), ('ttype','!=','one2many')]",
                                                string="Group By", help=' Define the x-axis of the graph. ')
    tele_chart_relation_sub_groupby = fields.Many2one('ir.model.fields',
                                                    domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),"
                                                           "('store','=',True),('ttype','!=','binary'),"
                                                           "('ttype','!=','many2many'), ('ttype','!=','one2many')]",
                                                    string=" Sub Group By",
                                                    help='Select the second level of grouping. ')
    tele_chart_date_groupby = fields.Selection([('minute', 'Minute'),
                                              ('hour', 'Hour'),
                                              ('day', 'Day'),
                                              ('week', 'Week'),
                                              ('month', 'Month'),
                                              ('quarter', 'Quarter'),
                                              ('year', 'Year'),
                                              ('month_year', 'Month-Year')
                                              ], string="Dashboard Item Chart Group By Type")
    tele_chart_date_sub_groupby = fields.Selection([('minute', 'Minute'),
                                                  ('hour', 'Hour'),
                                                  ('day', 'Day'),
                                                  ('week', 'Week'),
                                                  ('month', 'Month'),
                                                  ('quarter', 'Quarter'),
                                                  ('year', 'Year'),
                                                  ], string="Dashboard Item Chart Sub Group By Type")
    tele_graph_preview = fields.Char(string="Graph Preview", default="Graph Preview")
    tele_chart_data = fields.Char(string="Chart Data in string form", compute='tele_get_chart_data', compute_sudo=False)
    tele_chart_data_count_type = fields.Selection([('count', 'Count'), ('sum', 'Sum'), ('average', 'Average')],
                                                string="Data Type", default="sum")
    tele_chart_measure_field = fields.Many2many('ir.model.fields', 'tele_dn_measure_field_rel', 'measure_field_id',
                                              'field_id',
                                              domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),"
                                                     "('store','=',True),'|','|',"
                                                     "('ttype','=','integer'),('ttype','=','float'),"
                                                     "('ttype','=','monetary')]",
                                              string="Measure 1", help='Data points to be selected.')
    tele_chart_is_cumulative = fields.Boolean('Is Cumulative')
    tele_chart_cumulative_field = fields.Many2many('ir.model.fields', 'tele_dn_cumulative_measure_field_rel',
                                                 'measure_cumulative_field_id',
                                                 'cumulative_field_id',
                                                 domain="[('model_id','=',tele_model_id),('name','!=','id'),('name',"
                                                        "'!=','sequence'), "
                                                        "('store','=',True),'|','|',"
                                                        "('ttype','=','integer'),('ttype','=','float'),"
                                                        "('ttype','=','monetary')]",
                                                 string="Cumulative Fields", help='Data points to be selected.')

    tele_chart_cumulative = fields.Boolean("Cumulative As Line")
    tele_chart_measure_field_2 = fields.Many2many('ir.model.fields', 'tele_dn_measure_field_rel_2', 'measure_field_id_2',
                                                'field_id',
                                                domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),"
                                                       "('store','=',True),'|','|',"
                                                       "('ttype','=','integer'),('ttype','=','float'),"
                                                       "('ttype','=','monetary')]",
                                                string="Line Measure",
                                                help='Data Points displayed with a line in the graph. ')

    tele_bar_chart_stacked = fields.Boolean(string="Stacked Bar Chart", help='Stack the columns of the same record. ')

    tele_semi_circle_chart = fields.Boolean(string="Semi Circle Chart")

    tele_sort_by_field = fields.Many2one('ir.model.fields',
                                       domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),('store','=',True),"
                                              "('ttype','!=','one2many'),('ttype','!=','binary')]",
                                       string="Sort By Field", help='Select the desired sorting preference. ')
    tele_sort_by_order = fields.Selection([('ASC', 'Ascending'), ('DESC', 'Descending')],
                                        string="Sort Order", help=' Select the order of the sorting. ')
    tele_record_data_limit = fields.Integer(string="Record Limit", help=' Records to be displayed on the graph')

    tele_list_view_preview = fields.Char(string="List View Preview", default="List View Preview")

    tele_kpi_preview = fields.Char(string="Kpi Preview", default="KPI Preview")

    tele_kpi_type = fields.Selection([
        ('layout_1', 'KPI With Target'),
        ('layout_2', 'Data Comparison'),
    ], string="Kpi Layout", default="layout_1")

    tele_target_view = fields.Char(string="View", default="Number", help=' Select the view to compare target with data.')

    tele_data_comparison = fields.Char(string="Kpi Data Type", default="None")

    tele_kpi_data = fields.Char(string="KPI Data", compute="tele_get_kpi_data", compute_sudo=False)

    tele_chart_item_color = fields.Selection(
        [('default', 'Default'), ('cool', 'Cool'), ('warm', 'Warm'), ('neon', 'Neon')],
        string="Chart Color Palette", default="default", help='Select the display preference. ')

    # ------------------------ List View Fields ------------------------------

    tele_list_view_type = fields.Selection([('ungrouped', 'Un-Grouped'), ('grouped', 'Grouped')], default="ungrouped",
                                         string="List View Type", required=True,
                                         help='Select the desired list view type. ')
    tele_list_view_fields = fields.Many2many('ir.model.fields', 'tele_dn_list_field_rel', 'list_field_id', 'field_id',
                                           domain="[('model_id','=',tele_model_id),('ttype','!=','one2many'),"
                                                  "('ttype','!=','many2many'),('ttype','!=','binary')]",
                                           string="Fields to show in list",
                                           help=' Select the fields you want to display in the list.  ')

    tele_export_all_records = fields.Boolean(string="Export All Records", default=True,
                                           help="when click on boolean button, all the records will be downloaded which are present in entire list")

    tele_list_view_group_fields = fields.Many2many('ir.model.fields', 'tele_dn_list_group_field_rel', 'list_field_id',
                                                 'field_id',
                                                 domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),"
                                                        "('store','=',True),'|','|',"
                                                        "('ttype','=','integer'),('ttype','=','float'),"
                                                        "('ttype','=','monetary')]",
                                                 string="List View Grouped Fields")

    tele_list_view_data = fields.Char(string="List View Data in JSon", compute='tele_get_list_view_data',
                                    compute_sudo=False)

    # -------------------- Multi Company Feature ---------------------
    tele_company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,
                                    help='Name of the company for which analytics will be displayed in the dashboard. ')

    # -------------------- Target Company Feature ---------------------
    tele_goal_enable = fields.Boolean(string="Enable Target", help='Show the set target.')
    tele_goal_bar_line = fields.Boolean(string="Show Target As Line")
    tele_standard_goal_value = fields.Float(string="Standard Target", help='Show the set target')
    tele_goal_lines = fields.One2many('tele_dashboard_ninja.item_goal', 'tele_dashboard_item', string="Target Lines")

    tele_list_target_deviation_field = fields.Many2one('ir.model.fields', 'list_field_id',
                                                     domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),"
                                                            "('store','=',True),'|','|',"
                                                            "('ttype','=','integer'),('ttype','=','float'),"
                                                            "('ttype','=','monetary')]",
                                                     )

    tele_many2many_field_ordering = fields.Char()

    # TODO : Merge all these fields into one and show a widget to get output for these fields from JS
    tele_show_data_value = fields.Boolean(string="Show Data Value", help=' Display value on the graph. . ')

    tele_action_lines = fields.One2many('tele_dashboard_ninja.item_action', 'tele_dashboard_item_id', string="Action Lines")

    tele_actions = fields.Many2one('ir.actions.act_window', domain="[('res_model','=',tele_model_name)]",
                                 string="Actions", help="Redirects you to the selected view. ")

    tele_compare_period = fields.Integer(string="Include Period",
                                       help=' Provide the number of Date Filter Selection you want to include while displaying the record.')
    tele_year_period = fields.Integer(string="Same Period Previous Years",
                                    help=' Display the record for the same Date field for the last year. ')
    tele_compare_period_2 = fields.Integer(string="KPI Include Period")
    tele_year_period_2 = fields.Integer(string="KPI Same Period Previous Years")

    tele_multiplier_active = fields.Boolean(string="Apply Multiplier", default=False,
                                        help="Provides the visibility of multiplier field")
    tele_multiplier = fields.Float(string="Multiplier",default=1, help="Provides the multiplication of record value")



    # User can select custom units for measure
    tele_unit = fields.Boolean(string="Show Custom Unit", default=False, help='Display the unit of the data.')
    tele_unit_selection = fields.Selection([
        ('monetary', 'Monetary'),
        ('custom', 'Custom'),
    ], string="Select Unit Type", help='Select the unit to be assigned to the value. ')
    tele_chart_unit = fields.Char(string="Enter Unit", size=5, default="",
                                help="Maximum limit 5 characters, for ex: km, m")

    # User can stop propagation of the tile item
    tele_show_records = fields.Boolean(string="Show Records", default=True, help="""This field Enable the click on 
                                                                                  Dashboard Items to view the Tele 
                                                                                  default view of records""")
    #  Field for fill temp data
    tele_fill_temporal = fields.Boolean('Fill Temporal Value')
    # Domain Extension field
    tele_domain_extension = fields.Char('Domain Extension', help="Define conditions for filter to write manually")
    tele_domain_extension_2 = fields.Char('KPI Domain Extension')
    # hide legend
    tele_hide_legend = fields.Boolean('Show Legend', help="Hide all legend from the chart item", default=True)
    tele_data_calculation_type = fields.Selection([('custom', 'Default Query'),
                                                 ('query', 'Custom Query')], string="Data Calculation Type",
                                                default="custom",
                                                help='Select the type of calculation you want to perform on the data.')

    # to show the Global / Indian / Exact Number Format
    tele_data_format = fields.Selection([
        ('global', 'English Format'),
        ('indian', 'Indian Format'),
        ('colombian', 'Colombian Peso Format'),
        ('exact', 'Exact Value')],
        string='Number System',
        default='global',
        help="To Change the number format showing in chart to given option")
    tele_button_color = fields.Char(string="Top Button Color",
                                  default="#000000,0.99")


    tele_is_client_action = fields.Boolean('Client Action', default=False)
    tele_client_action = fields.Many2one('ir.actions.client',
                                       string="Client Item Action",
                                       domain="[('name','!=','App Store'),('name','!=','Updates')]",
                                       help="This Action will be Performed at the end of Drill Down Action")
    tele_pagination_limit = fields.Integer('Pagination Limit', default=15)

    tele_multiplier_lines = fields.One2many('tele_dashboard_item.multiplier', 'tele_dashboard_item_id',

                                          readonly=False, store=True,
                                          string="Multiplier Lines")

    tele_precision_digits = fields.Integer('Digits', compute="_tele_compute_precision_digits", store=True, readonly=False)

    tele_data_label_type = fields.Selection([('percent', 'Percent'), ('value', 'Value')], string='Show Data Value Type',
                                          help='When "Show Data Value Type" selected this field enables to select label type in percent or value',
                                          default='percent')

    @api.onchange('tele_year_period', 'tele_year_period_2')
    def tele_year_neg_val_not_allow(self):
        for rec in self:
            if rec.tele_year_period < 0 or rec.tele_year_period_2 < 0 :
                raise ValidationError(_(" Negative periods are not allowed "))

    @api.onchange('tele_item_start_date', 'tele_item_end_date')
    def tele_item_date_validation(self):
        for rec in self:
            if rec.tele_item_start_date and rec.tele_item_end_date:
                if rec.tele_item_start_date > rec.tele_item_end_date:
                    raise ValidationError(_('Start date must be less than end date'))

    @api.onchange('tele_item_start_date_2', 'tele_item_end_date_2')
    def tele_item_date_validation_2(self):
        for rec in self:
            if rec.tele_item_start_date_2 and rec.tele_item_end_date_2:
                if rec.tele_item_start_date_2 > rec.tele_item_end_date_2:
                    raise ValidationError(_('Start date must be less than end date'))

    @api.depends('tele_dashboard_item_type')
    def _tele_compute_precision_digits(self):
        for rec in self:
            try:
                precision_digits = self.sudo().env.ref('tele_dashboard_ninja.tele_dashboard_ninja_precision')
                tele_precision_digits = precision_digits.digits
                if tele_precision_digits < 0:
                    tele_precision_digits = 2
                if tele_precision_digits > 100:
                    tele_precision_digits = 2

                rec.tele_precision_digits = tele_precision_digits
            except Exception as E:
                rec.tele_precision_digits = 2
    # default = lambda self: self.sudo().env.ref('tele_dashboard_ninja.tele_dashboard_ninja_precision')

    @api.onchange('tele_multiplier_active', 'tele_chart_measure_field',
                  'tele_chart_measure_field_2' ,'tele_list_view_group_fields')
    def _tele_compute_multiplier_lines(self):
        for rec in self:
            rec.tele_multiplier_lines = [(5, 0, 0)]
            tele_chart_measure_fields = rec.tele_chart_measure_field
            if rec.tele_multiplier_active:
                if rec.tele_dashboard_item_type == 'tele_list_view' and rec.tele_list_view_type == 'grouped':
                    tele_chart_measure_fields = rec.tele_list_view_group_fields
                tele_temp_list = []
                tele_chart_measure_id = []
                for tele_chart_measure_field in tele_chart_measure_fields:
                    tele_dict = {
                        'tele_dashboard_item_id': rec.id,
                        'tele_multiplier_fields': tele_chart_measure_field.ids[0],
                        'tele_multiplier_value': 1
                    }
                    tele_chart_measure_id.append(tele_chart_measure_field.ids[0])
                    tele_line = self.env['tele_dashboard_item.multiplier'].create(tele_dict)
                    tele_temp_list.append(tele_line.id)

                if rec.tele_chart_measure_field_2:
                    for tele_chart_measure_field in rec.tele_chart_measure_field_2:
                        if tele_chart_measure_field.ids[0] not in tele_chart_measure_id:
                            tele_dict = {
                                'tele_dashboard_item_id': rec.id,
                                'tele_multiplier_fields': tele_chart_measure_field.ids[0],
                                'tele_multiplier_value': 1
                            }
                            tele_line = self.env['tele_dashboard_item.multiplier'].create(tele_dict)
                            tele_temp_list.append(tele_line.id)
                    # rec.tele_multiplier_lines = [(6, 0, [])]
                    # rec.tele_multiplier_lines = [(6, 0, tele_temp_list)]
                rec.tele_multiplier_lines = [(6, 0, [])]
                rec.tele_multiplier_lines = [(6, 0, tele_temp_list)]

            if len(rec.tele_chart_measure_field) == 0:
                rec.tele_chart_cumulative_field = False





    @api.onchange('tele_list_view_type')
    def _tele_onchange_tele_list_view_type(self):
        for rec in self:
            if rec.tele_list_view_type == 'ungrouped':
                rec.tele_multiplier_active = False

    @api.onchange('tele_data_calculation_type')
    def _tele_onchange_tele_data_calculation_type(self):
        for rec in self:
            if rec.tele_data_calculation_type == 'query':
                rec.tele_list_view_type = 'ungrouped'
                rec.tele_multiplier_active = False

    @api.onchange('tele_goal_lines')
    def tele_is_goal_lines(self):
        for rec in self:
            if rec.tele_goal_enable and rec.tele_goal_lines:
                rec.tele_pagination_limit = 0
            elif rec.tele_goal_enable and not rec.tele_goal_lines:
                rec.tele_pagination_limit = 15


    @api.onchange('tele_goal_enable')
    def tele_is_goal_enable(self):
        for rec in self:
            if not rec.tele_goal_enable :
                rec.tele_goal_lines = False
                rec.tele_pagination_limit = 15
            elif rec.tele_goal_enable and not rec.tele_goal_lines:
                rec.tele_pagination_limit = 15


    @api.onchange('tele_pagination_limit')
    def tele_on_negativ_limit(self):
        for rec in self:
            if rec.tele_pagination_limit > 0:
                rec.tele_pagination_limit = rec.tele_pagination_limit
            elif not rec.tele_goal_lines and rec.tele_pagination_limit <= 0:
                raise ValidationError(_("Pagination limit value cannot be Negative or Zero"))
            if rec.tele_goal_lines and rec.tele_pagination_limit > 0 or rec.tele_pagination_limit < 0:
                raise ValidationError(_("if target lines is selected then cannot be set pagination value"))

    @api.onchange('tele_is_client_action')
    def tele_on_change_item_action_to_client(self):
        for rec in self:
            if rec.tele_is_client_action:
                rec.tele_actions = False

    @api.onchange('tele_record_data_limit_visibility')
    def tele_on_change_record_data_visibility(self):
        for rec in self:
            if not rec.tele_record_data_limit_visibility:
                rec.tele_record_data_limit = 0



    @api.onchange('tele_fill_temporal')
    def tele_onchange_fill_temporal(self):
        if self.tele_fill_temporal:
            self.tele_sort_by_field = self.tele_chart_relation_groupby.id
            self.tele_sort_by_order = 'ASC'
        else:
            self.tele_sort_by_field = False
            self.tele_sort_by_order = False

    @api.onchange('tele_goal_lines')
    def tele_date_target_line(self):
        for rec in self:
            if rec.tele_chart_date_groupby in ('minute', 'hour') or rec.tele_chart_date_sub_groupby in ('minute', 'hour'):
                rec.tele_goal_lines = False
                return {'warning': {
                    'title': _('Groupby Field aggregation'),
                    'message': _(
                        'Cannot create target lines when Group By Date field is set to have aggregation in '
                        'Minute and Hour case.')
                }}

    @api.onchange('tele_chart_date_groupby', 'tele_chart_date_sub_groupby')
    def tele_date_target(self):
        for rec in self:
            if (rec.tele_chart_date_groupby in ('minute', 'hour') or rec.tele_chart_date_sub_groupby in ('minute', 'hour')) \
                    and rec.tele_goal_lines:
                raise ValidationError(_(
                    "Cannot set aggregation having Date time (Hour, Minute) when target lines per date are being used."
                    " To proceed this, first delete target lines"))
            if rec.tele_chart_relation_groupby.ttype == 'date' and rec.tele_chart_date_groupby in ('minute', 'hour'):
                raise ValidationError(_('Groupby field: {} cannot be aggregated by {}').format(
                    rec.tele_chart_relation_groupby.display_name, rec.tele_chart_date_groupby))
            if rec.tele_chart_relation_sub_groupby.ttype == 'date' and rec.tele_chart_date_sub_groupby in (
                    'minute', 'hour'):
                raise ValidationError(_('Groupby field: {} cannot be aggregated by {}').format(
                    rec.tele_chart_relation_sub_groupby.display_name, rec.tele_chart_date_sub_groupby))

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'tele_action_lines' not in default:
            default['tele_action_lines'] = [(0, 0, line.copy_data()[0]) for line in self.tele_action_lines]

        if 'tele_goal_lines' not in default:
            default['tele_goal_lines'] = [(0, 0, line.copy_data()[0]) for line in self.tele_goal_lines]
        tele_many2many_field_ordering = self.tele_many2many_field_ordering
        tele_list_view_group_fields = []
        tele_list_view_fields = []
        tele_chart_measure_field = []
        tele_chart_measure_field_2 = []
        if tele_many2many_field_ordering:
            tele_many2many_field_ordering = json.loads(tele_many2many_field_ordering)
            tele_list_view_group_fields = tele_many2many_field_ordering.get('tele_list_view_group_fields', False)
            tele_list_view_fields = tele_many2many_field_ordering.get('tele_list_view_fields', False)
            tele_chart_measure_field = tele_many2many_field_ordering.get('tele_chart_measure_field', False)
            tele_chart_measure_field_2 = tele_many2many_field_ordering.get('tele_chart_measure_field_2', False)
        if 'tele_list_view_group_fields' not in default:
            default['tele_list_view_group_fields'] = tele_list_view_group_fields
        if 'tele_list_view_fields' not in default:
            default['tele_list_view_fields'] = tele_list_view_fields
        if 'tele_chart_measure_field' not in default:
            default['tele_chart_measure_field'] = tele_chart_measure_field
        if 'tele_chart_measure_field_2' not in default:
            default['tele_chart_measure_field_2'] = tele_chart_measure_field_2
        return super(TeleDashboardNinjaItems, self).copy_data(default)

    def copy(self, default=None):
        default = default or {}
        res = super(TeleDashboardNinjaItems, self).copy(default)

        if self.tele_dn_header_lines:
            for line in self.tele_dn_header_lines:
                tele_line = {}
                tele_line['tele_to_do_header'] = line.tele_to_do_header
                tele_line['tele_dn_item_id'] = res.id
                tele_dn_header_id = self.env['tele_to.do.headers'].create(tele_line)
                if line.tele_to_do_description_lines:
                    for tele_task in line.tele_to_do_description_lines:
                        tele_task_line = {
                            'tele_to_do_header_id': tele_dn_header_id.id,
                            'tele_description': tele_task.tele_description,
                            'tele_active': tele_task.tele_active
                        }

                        self.env['tele_to.do.description'].create(tele_task_line)
        return res

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if not name:
                name = rec.tele_model_id.name
            res.append((rec.id, name))

        return res

    @api.model
    def create(self, values):
        """ Override to save list view fields ordering """
        if not values.get('tele_many2many_field_ordering', False):
            tele_list_view_group_fields_name = []
            tele_list_view_fields_name = []
            tele_chart_measure_field_name = []
            tele_chart_measure_field_2_name = []
            if values.get('tele_list_view_group_fields', False) and len(values['tele_list_view_group_fields'][0][2]) > 0:
                for measure in values['tele_list_view_group_fields'][0][2]:
                    tele_measure_id = self.env['ir.model.fields'].search(
                        [('id', '=', measure)])
                    tele_list_view_group_fields_name.append(tele_measure_id.name)
            if values.get('tele_list_view_fields', False) and len(values['tele_list_view_fields'][0][2]) > 0:
                for measure in values['tele_list_view_fields'][0][2]:
                    tele_measure_id = self.env['ir.model.fields'].search(
                        [('id', '=', measure)])
                    tele_list_view_fields_name.append(tele_measure_id.name)
            if values.get('tele_chart_measure_field', False) and len(values['tele_chart_measure_field'][0][2]) > 0:
                for measure in values['tele_chart_measure_field'][0][2]:
                    tele_measure_id = self.env['ir.model.fields'].search(
                        [('id', '=', measure)])
                    tele_chart_measure_field_name.append(tele_measure_id.name)
            if values.get('tele_chart_measure_field_2', False) and len(values['tele_chart_measure_field_2'][0][2]) > 0:
                for measure in values['tele_chart_measure_field_2'][0][2]:
                    tele_measure_id = self.env['ir.model.fields'].search(
                        [('id', '=', measure)])
                    tele_chart_measure_field_2_name.append(tele_measure_id.name)
            tele_many2many_field_ordering = {
                'tele_list_view_fields': values['tele_list_view_fields'][0][2] if values.get('tele_list_view_fields', False) else [],
                'tele_list_view_fields_name': tele_list_view_fields_name,
                'tele_list_view_group_fields': values['tele_list_view_group_fields'][0][2] if values.get('tele_list_view_group_fields', False) else [],
                'tele_list_view_group_fields_name': tele_list_view_group_fields_name ,
                'tele_chart_measure_field': values['tele_chart_measure_field'][0][2] if values.get('tele_chart_measure_field', False) else [],
                'tele_chart_measure_field_name': tele_chart_measure_field_name,
                'tele_chart_measure_field_2': values['tele_chart_measure_field_2'][0][2] if values.get('tele_chart_measure_field_2', False) else [],
                'tele_chart_measure_field_2_name': tele_chart_measure_field_2_name,
            }
            values['tele_many2many_field_ordering'] = json.dumps(tele_many2many_field_ordering)

        return super(TeleDashboardNinjaItems, self).create(
            values)

    @api.onchange('tele_list_view_fields')
    def tele_list_view_fields_onchange(self):
        tele_many2many_field_ordering = {}
        for rec in self:
            if rec.tele_many2many_field_ordering:
                tele_many2many_field_ordering = json.loads(rec.tele_many2many_field_ordering)
            tele_many2many_field_ordering['tele_list_view_fields'] = rec.tele_list_view_fields.ids
            tele_many2many_field_ordering['tele_list_view_fields_name'] = [x.name for x in rec.tele_list_view_fields]

            rec.tele_many2many_field_ordering = json.dumps(tele_many2many_field_ordering)

    @api.onchange('tele_list_view_group_fields')
    def tele_list_view_group_fields_onchange(self):
        tele_many2many_field_ordering = {}
        for rec in self:
            if rec.tele_many2many_field_ordering:
                tele_many2many_field_ordering = json.loads(rec.tele_many2many_field_ordering)
            tele_many2many_field_ordering['tele_list_view_group_fields'] = rec.tele_list_view_group_fields.ids
            tele_many2many_field_ordering['tele_list_view_group_fields_name'] = [x.name for x in rec.tele_list_view_group_fields]
            rec.tele_many2many_field_ordering = json.dumps(tele_many2many_field_ordering)

    @api.onchange('tele_chart_measure_field')
    def tele_chart_measure_field_onchange(self):
        for rec in self:
            tele_many2many_field_ordering = {}
            if rec.tele_many2many_field_ordering:
                tele_many2many_field_ordering = json.loads(rec.tele_many2many_field_ordering)
            tele_many2many_field_ordering['tele_chart_measure_field'] = rec.tele_chart_measure_field.ids
            tele_many2many_field_ordering['tele_chart_measure_field_name'] = [x.name for x in
                                                                             rec.tele_chart_measure_field]
            rec.tele_many2many_field_ordering = json.dumps(tele_many2many_field_ordering)

    @api.onchange('tele_chart_measure_field_2')
    def tele_chart_measure_field_2_onchange(self):
        tele_many2many_field_ordering = {}
        for rec in self:
            if rec.tele_many2many_field_ordering:
                tele_many2many_field_ordering = json.loads(rec.tele_many2many_field_ordering)
            tele_many2many_field_ordering['tele_chart_measure_field_2'] = rec.tele_chart_measure_field_2.ids
            tele_many2many_field_ordering['tele_chart_measure_field_2_name'] = [x.name for x in
                                                                          rec.tele_chart_measure_field_2]
            rec.tele_many2many_field_ordering = json.dumps(tele_many2many_field_ordering)



    @api.onchange('tele_layout')
    def layout_four_font_change(self):
        if self.tele_dashboard_item_theme != "white":
            if self.tele_layout == 'layout4':
                self.tele_font_color = self.tele_background_color
                self.tele_default_icon_color = "#ffffff,0.99"
            elif self.tele_layout == 'layout6':
                self.tele_font_color = "#ffffff,0.99"
                self.tele_default_icon_color = self.tele_get_dark_color(self.tele_background_color.split(',')[0],
                                                                    self.tele_background_color.split(',')[1])
            else:
                self.tele_default_icon_color = "#ffffff,0.99"
                self.tele_font_color = "#ffffff,0.99"
        else:
            if self.tele_layout == 'layout4':
                self.tele_background_color = "#00000,0.99"
                self.tele_font_color = self.tele_background_color
                self.tele_default_icon_color = "#ffffff,0.99"
            else:
                self.tele_background_color = "#ffffff,0.99"
                self.tele_font_color = "#00000,0.99"
                self.tele_default_icon_color = "#00000,0.99"

    # To convert color into 10% darker. Percentage amount is hardcoded. Change amt if want to change percentage.
    def tele_get_dark_color(self, color, opacity):
        num = int(color[1:], 16)
        amt = -25
        R = (num >> 16) + amt
        R = (255 if R > 255 else 0 if R < 0 else R) * 0x10000
        G = (num >> 8 & 0x00FF) + amt
        G = (255 if G > 255 else 0 if G < 0 else G) * 0x100
        B = (num & 0x0000FF) + amt
        B = (255 if B > 255 else 0 if B < 0 else B)
        return "#" + hex(0x1000000 + R + G + B).split('x')[1][1:] + "," + opacity

    @api.onchange('tele_model_id')
    def make_record_field_empty(self):
        for rec in self:
            rec.tele_record_field = False
            rec.tele_domain = False
            rec.tele_date_filter_field = False
            # To show "created on" by default on date filter field on model select.
            if rec.tele_model_id:
                datetime_field_list = rec.tele_date_filter_field.search(
                    [('model_id', '=', rec.tele_model_id.id), '|', ('ttype', '=', 'date'),
                     ('ttype', '=', 'datetime')]).read(['id', 'name'])
                for field in datetime_field_list:
                    if field['name'] == 'create_date':
                        rec.tele_date_filter_field = field['id']
            else:
                rec.tele_date_filter_field = False
            # Pro
            rec.tele_record_field = False
            rec.tele_chart_measure_field = False
            rec.tele_chart_measure_field_2 = False
            rec.tele_chart_relation_sub_groupby = False
            rec.tele_chart_relation_groupby = False
            rec.tele_chart_date_sub_groupby = False
            rec.tele_chart_date_groupby = False
            rec.tele_sort_by_field = False
            rec.tele_sort_by_order = False
            rec.tele_record_data_limit = False
            rec.tele_list_view_fields = False
            rec.tele_list_view_group_fields = False
            rec.tele_action_lines = False
            rec.tele_actions = False
            rec.tele_domain_extension = False

    @api.onchange('tele_record_count', 'tele_layout', 'name', 'tele_model_id', 'tele_domain', 'tele_icon_select',
                  'tele_default_icon', 'tele_icon',
                  'tele_background_color', 'tele_font_color', 'tele_default_icon_color')
    def tele_preview_update(self):
        self.tele_preview += 1

    @api.onchange('tele_dashboard_item_theme')
    def change_dashboard_item_theme(self):
        if self.tele_dashboard_item_theme == "red":
            self.tele_background_color = "#d9534f,0.99"
            self.tele_default_icon_color = "#ffffff,0.99"
            self.tele_font_color = "#ffffff,0.99"
            self.tele_button_color = "#000000,0.99"
        elif self.tele_dashboard_item_theme == "blue":
            self.tele_background_color = "#337ab7,0.99"
            self.tele_default_icon_color = "#ffffff,0.99"
            self.tele_font_color = "#ffffff,0.99"
            self.tele_button_color = "#000000,0.99"
        elif self.tele_dashboard_item_theme == "yellow":
            self.tele_background_color = "#f0ad4e,0.99"
            self.tele_default_icon_color = "#ffffff,0.99"
            self.tele_font_color = "#ffffff,0.99"
            self.tele_button_color = "#000000,0.99"
        elif self.tele_dashboard_item_theme == "green":
            self.tele_background_color = "#5cb85c,0.99"
            self.tele_default_icon_color = "#ffffff,0.99"
            self.tele_font_color = "#ffffff,0.99"
            self.tele_button_color = "#000000,0.99"
        elif self.tele_dashboard_item_theme == "white":
            if self.tele_layout == 'layout4':
                self.tele_background_color = "#00000,0.99"
                self.tele_default_icon_color = "#ffffff,0.99"
                self.tele_button_color = "#000000,0.99"
            else:
                self.tele_background_color = "#ffffff,0.99"
                self.tele_default_icon_color = "#000000,0.99"
                self.tele_font_color = "#000000,0.99"
                self.tele_button_color = "#000000,0.99"

        if self.tele_layout == 'layout4':
            self.tele_font_color = self.tele_background_color

        elif self.tele_layout == 'layout6':
            self.tele_default_icon_color = self.tele_get_dark_color(self.tele_background_color.split(',')[0],
                                                                self.tele_background_color.split(',')[1])
            if self.tele_dashboard_item_theme == "white":
                self.tele_default_icon_color = "#000000,0.99"

    @api.depends('tele_record_count_type', 'tele_model_id', 'tele_domain', 'tele_record_field', 'tele_date_filter_field',
                 'tele_item_end_date', 'tele_item_start_date', 'tele_compare_period', 'tele_year_period',
                 'tele_dashboard_item_type', 'tele_domain_extension', 'tele_data_format')
    def tele_get_record_count(self):
        for rec in self:
            rec.tele_record_count = rec._teleGetRecordCount(domain=[])

    def _teleGetRecordCount(self, domain=[]):
        rec = self
        if rec.tele_record_count_type == 'count' or rec.tele_dashboard_item_type == 'tele_list_view':
            tele_record_count = rec.tele_fetch_model_data(rec.tele_model_name, rec.tele_domain, 'search_count', rec, domain)
        elif rec.tele_record_count_type in ['sum',
                                          'average'] and rec.tele_record_field and rec.tele_dashboard_item_type != 'tele_list_view':
            tele_records_grouped_data = rec.tele_fetch_model_data(rec.tele_model_name, rec.tele_domain, 'read_group', rec,
                                                              domain)
            if tele_records_grouped_data and len(tele_records_grouped_data) > 0:
                tele_records_grouped_data = tele_records_grouped_data[0]
                if rec.tele_record_count_type == 'sum' and tele_records_grouped_data.get('__count', False) and (
                        tele_records_grouped_data.get(rec.tele_record_field.name)):
                    tele_record_count = tele_records_grouped_data.get(rec.tele_record_field.name, 0)
                elif rec.tele_record_count_type == 'average' and tele_records_grouped_data.get(
                        '__count', False) and (tele_records_grouped_data.get(rec.tele_record_field.name)):
                    tele_record_count = tele_records_grouped_data.get(rec.tele_record_field.name,
                                                                  0) / tele_records_grouped_data.get('__count',
                                                                                                   1)
                else:
                    tele_record_count = 0
            else:
                tele_record_count = 0
        else:
            tele_record_count = 0
        return tele_record_count

    # Writing separate function to fetch dashboard item data
    def tele_fetch_model_data(self, tele_model_name, tele_domain, tele_func, rec, domain=[]):
        data = 0
        try:
            if tele_domain and tele_domain != '[]' and tele_model_name:
                proper_domain = self.tele_convert_into_proper_domain(tele_domain, rec, domain)
                if tele_func == 'search_count':
                    data = self.env[tele_model_name].search_count(proper_domain)
                elif tele_func == 'read_group':
                    data = self.env[tele_model_name].read_group(proper_domain, [rec.tele_record_field.name], [], lazy=False)
            elif tele_model_name:
                # Have to put extra if condition here because on load,model giving False value
                proper_domain = self.tele_convert_into_proper_domain(False, rec, domain)
                if tele_func == 'search_count':
                    data = self.env[tele_model_name].search_count(proper_domain)

                elif tele_func == 'read_group':
                    data = self.env[tele_model_name].read_group(proper_domain, [rec.tele_record_field.name], [], lazy=False)
            else:
                return []
        except Exception as e:
            return 0
        return data

    def tele_convert_into_proper_domain(self, tele_domain, rec, domain=[]):
        if tele_domain and "%UID" in tele_domain:
            tele_domain = tele_domain.replace('"%UID"', str(self.env.user.id))

        if tele_domain and "%MYCOMPANY" in tele_domain:
            tele_domain = tele_domain.replace('"%MYCOMPANY"', str(self.env.company.id))

        tele_date_domain = False
        if rec.tele_date_filter_field:
            if not rec.tele_date_filter_selection or rec.tele_date_filter_selection == "l_none":
                selected_start_date = self._context.get('teleDateFilterStartDate', False)
                selected_end_date = self._context.get('teleDateFilterEndDate', False)
                tele_is_def_custom_filter = self._context.get('teleIsDefultCustomDateFilter', False)
                tele_timezone = self._context.get('tz') or self.env.user.tz
                if selected_start_date and selected_end_date and rec.tele_date_filter_field.ttype == 'datetime' and not tele_is_def_custom_filter:
                    selected_start_date = tele_convert_into_utc(selected_start_date, tele_timezone)
                    selected_end_date = tele_convert_into_utc(selected_end_date, tele_timezone)
                if selected_start_date and selected_end_date and rec.tele_date_filter_field.ttype == 'date' and tele_is_def_custom_filter:
                    selected_start_date = tele_convert_into_local(selected_start_date, tele_timezone)
                    selected_end_date = tele_convert_into_local(selected_end_date, tele_timezone)

                if self._context.get('teleDateFilterSelection', False) and self._context['teleDateFilterSelection'] not in [
                    'l_none', 'l_custom']:
                    tele_date_data = tele_get_date(self._context.get('teleDateFilterSelection'), self,
                                               rec.tele_date_filter_field.ttype)
                    selected_start_date = tele_date_data["selected_start_date"]
                    selected_end_date = tele_date_data["selected_end_date"]

                if selected_end_date and not selected_start_date:
                    tele_date_domain = [
                        (rec.tele_date_filter_field.name, "<=",
                         selected_end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
                elif selected_start_date and not selected_end_date:
                    tele_date_domain = [
                        (rec.tele_date_filter_field.name, ">=",
                         selected_start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
                else:
                    if selected_end_date and selected_start_date:
                        tele_date_domain = [
                            (rec.tele_date_filter_field.name, ">=",
                             selected_start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                            (rec.tele_date_filter_field.name, "<=",
                             selected_end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]

            else:
                if rec.tele_date_filter_selection and rec.tele_date_filter_selection != 'l_custom':
                    tele_date_data = tele_get_date(rec.tele_date_filter_selection, self, rec.tele_date_filter_field.ttype)
                    selected_start_date = tele_date_data["selected_start_date"]
                    selected_end_date = tele_date_data["selected_end_date"]
                else:
                    selected_start_date = False
                    selected_end_date = False
                    if rec.tele_item_start_date or rec.tele_item_end_date:
                        selected_start_date = rec.tele_item_start_date
                        selected_end_date = rec.tele_item_end_date
                        if rec.tele_date_filter_field.ttype == 'date' and rec.tele_item_start_date and rec.tele_item_end_date:
                            tele_timezone = self._context.get('tz') or self.env.user.tz
                            selected_start_date = tele_convert_into_local(rec.tele_item_start_date, tele_timezone)
                            selected_end_date = tele_convert_into_local(rec.tele_item_end_date, tele_timezone)

                if selected_start_date and selected_end_date:
                    if rec.tele_compare_period:
                        tele_compare_period = abs(rec.tele_compare_period)
                        if tele_compare_period > 100:
                            tele_compare_period = 100
                        if rec.tele_compare_period > 0:
                            selected_end_date = selected_end_date + (
                                    selected_end_date - selected_start_date) * tele_compare_period
                            if rec.tele_date_filter_field.ttype == "date" and rec.tele_date_filter_selection == 'l_day':
                                selected_end_date = selected_end_date + timedelta(days=tele_compare_period)
                        elif rec.tele_compare_period < 0:
                            selected_start_date = selected_start_date - (
                                    selected_end_date - selected_start_date) * tele_compare_period
                            if rec.tele_date_filter_field.ttype == "date" and rec.tele_date_filter_selection == 'l_day':
                                selected_start_date = selected_end_date - timedelta(days=tele_compare_period)

                    if rec.tele_year_period and rec.tele_year_period != 0 and rec.tele_dashboard_item_type:
                        abs_year_period = abs(rec.tele_year_period)
                        sign_yp = rec.tele_year_period / abs_year_period
                        if abs_year_period > 100:
                            abs_year_period = 100
                        date_field_name = rec.tele_date_filter_field.name

                        tele_date_domain = ['&', (date_field_name, ">=",
                                                fields.datetime.strftime(selected_start_date,
                                                                         DEFAULT_SERVER_DATETIME_FORMAT)),
                                          (date_field_name, "<=",
                                           fields.datetime.strftime(selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT))]

                        for p in range(1, abs_year_period + 1):
                            tele_date_domain.insert(0, '|')
                            tele_date_domain.extend(['&', (date_field_name, ">=", fields.datetime.strftime(
                                selected_start_date - relativedelta.relativedelta(years=p) * sign_yp,
                                DEFAULT_SERVER_DATETIME_FORMAT)),
                                                   (date_field_name, "<=", fields.datetime.strftime(
                                                       selected_end_date - relativedelta.relativedelta(years=p)
                                                       * sign_yp, DEFAULT_SERVER_DATETIME_FORMAT))])
                    else:
                        selected_start_date = fields.datetime.strftime(selected_start_date,
                                                                       DEFAULT_SERVER_DATETIME_FORMAT)
                        selected_end_date = fields.datetime.strftime(selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                        tele_date_domain = [(rec.tele_date_filter_field.name, ">=", selected_start_date),
                                          (rec.tele_date_filter_field.name, "<=", selected_end_date)]
                elif selected_start_date and not selected_end_date:
                    selected_start_date = fields.datetime.strftime(selected_start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    tele_date_domain = [(rec.tele_date_filter_field.name, ">=", selected_start_date)]
                elif selected_end_date and not selected_start_date:
                    selected_end_date = fields.datetime.strftime(selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    tele_date_domain = [(rec.tele_date_filter_field.name, "<=", selected_end_date)]
        else:
            tele_date_domain = []

        proper_domain = safe_eval(tele_domain) if tele_domain else []
        if tele_date_domain:
            proper_domain.extend(tele_date_domain)
        if rec.tele_domain_extension:
            tele_domain_extension = rec.tele_convert_domain_extension(rec.tele_domain_extension, rec)
            proper_domain.extend(tele_domain_extension)
        if domain:
            proper_domain.extend(domain)

        return proper_domain

    def tele_convert_domain_extension(self, tele_extensiom_domain, rec):
        if tele_extensiom_domain and "%UID" in tele_extensiom_domain:
            tele_extensiom_domain = tele_extensiom_domain.replace('"%UID"', str(self.env.user.id))
            if "%UID" in tele_extensiom_domain:
                tele_extensiom_domain = tele_extensiom_domain.replace("'%UID'", str(self.env.user.id))
                print(tele_extensiom_domain)

        if tele_extensiom_domain and "%MYCOMPANY" in tele_extensiom_domain:
            tele_extensiom_domain = tele_extensiom_domain.replace('"%MYCOMPANY"', str(self.env.company.id))
            if "%MYCOMPANY" in tele_extensiom_domain:
                tele_extensiom_domain = tele_extensiom_domain.replace("'%MYCOMPANY'", str(self.env.company.id))

        tele_domain = eval(tele_extensiom_domain)
        return tele_domain

    @api.onchange('tele_domain_extension')
    def tele_onchange_domain_extension(self):
        if self.tele_domain_extension:
            proper_domain = []
            try:
                tele_domain_extension = self.tele_domain_extension
                if "%UID" in tele_domain_extension:
                    tele_domain_extension = tele_domain_extension.replace("%UID", str(self.env.user.id))
                if "%MYCOMPANY" in tele_domain_extension:
                    tele_domain_extension = tele_domain_extension.replace("%MYCOMPANY", str(self.env.company.id))
                self.env[self.tele_model_name].search_count(safe_eval(tele_domain_extension))
            except Exception:
                raise ValidationError(
                    "Domain Extension Syntax is wrong. \nProper Syntax Example :[['<field_name'>,'<operator>','"
                    "<value_to_compare>']]")

    @api.constrains('tele_domain_extension')
    def tele_check_domain_extension(self):
        if self.tele_domain_extension:
            proper_domain = []
            try:
                tele_domain_extension = self.tele_domain_extension
                if "%UID" in tele_domain_extension:
                    tele_domain_extension = tele_domain_extension.replace("%UID", str(self.env.user.id))
                if "%MYCOMPANY" in tele_domain_extension:
                    tele_domain_extension = tele_domain_extension.replace("%MYCOMPANY", str(self.env.company.id))
                self.env[self.tele_model_name].search_count(safe_eval(tele_domain_extension))
            except Exception:
                raise ValidationError(
                    "Domain Extension Syntax is wrong. \nProper Syntax Example :[['<field_name'>,'<operator>',"
                    "'<value_to_compare>']]")

    @api.onchange('tele_domain_extension_2')
    def tele_onchange_domain_extension_2(self):
        if self.tele_domain_extension_2:
            proper_domain = []
            try:
                tele_domain_extension = self.tele_domain_extension_2
                if "%UID" in tele_domain_extension:
                    tele_domain_extension = tele_domain_extension.replace("%UID", str(self.env.user.id))
                if "%MYCOMPANY" in tele_domain_extension:
                    tele_domain_extension = tele_domain_extension.replace("%MYCOMPANY", str(self.env.company.id))
                self.env[self.tele_model_name].search_count(safe_eval(tele_domain_extension))
            except Exception:
                raise ValidationError(
                    "Domain Extension Syntax is wrong. \nProper Syntax Example :[['<field_name'>,'<operator>',"
                    "'<value_to_compare>']]")

    @api.constrains('tele_domain_extension_2')
    def tele_check_domain_extension_2(self):
        if self.tele_domain_extension:
            proper_domain = []
            try:
                tele_domain_extension = self.tele_domain_extension
                if "%UID" in tele_domain_extension:
                    tele_domain_extension = tele_domain_extension.replace("%UID", str(self.env.user.id))
                if "%MYCOMPANY" in tele_domain_extension:
                    tele_domain_extension = tele_domain_extension.replace("%MYCOMPANY", str(self.env.company.id))
                self.env[self.tele_model_name].search_count(safe_eval(tele_domain_extension))
            except Exception:
                raise ValidationError(
                    "Domain Extension Syntax is wrong. \nProper Syntax Example :[['<field_name'>,'<operator>',"
                    "'<value_to_compare>']]")

    @api.depends('tele_chart_relation_groupby')
    def get_chart_groupby_type(self):
        for rec in self:
            if rec.tele_chart_relation_groupby.ttype == 'datetime' or rec.tele_chart_relation_groupby.ttype == 'date':
                rec.tele_chart_groupby_type = 'date_type'
            elif rec.tele_chart_relation_groupby.ttype == 'many2one':
                rec.tele_chart_groupby_type = 'relational_type'
                rec.tele_chart_date_groupby = False
            elif rec.tele_chart_relation_groupby.ttype == 'selection':
                rec.tele_chart_groupby_type = 'selection'
                rec.tele_chart_date_groupby = False
            else:
                rec.tele_chart_groupby_type = 'other'

    @api.onchange('tele_chart_relation_groupby')
    def tele_empty_sub_group_by(self):
        for rec in self:
            if not rec.tele_chart_relation_groupby or rec.tele_chart_groupby_type == "date_type" \
                    and not rec.tele_chart_date_groupby:
                rec.tele_chart_relation_sub_groupby = False
                rec.tele_chart_date_sub_groupby = False
            if not (rec.tele_chart_relation_groupby.ttype == 'datetime' or \
                    rec.tele_chart_relation_groupby.ttype == 'date'):
                rec.tele_goal_lines = False
                rec.tele_goal_enable = False
                rec.tele_fill_temporal = False





    @api.onchange('tele_chart_relation_sub_groupby', 'tele_fill_temporal', 'tele_goal_lines')
    def tele_empty_limit(self):
        for rec in self:
            if rec.tele_chart_relation_sub_groupby or rec.tele_fill_temporal or rec.tele_goal_lines:
                rec.tele_record_data_limit = 0
            if rec.tele_chart_relation_sub_groupby:
                rec.tele_chart_cumulative_field = False
                rec.tele_fill_temporal = False

    @api.depends('tele_chart_relation_sub_groupby')
    def get_chart_sub_groupby_type(self):
        for rec in self:
            if rec.tele_chart_relation_sub_groupby.ttype == 'datetime' or \
                    rec.tele_chart_relation_sub_groupby.ttype == 'date':
                rec.tele_chart_sub_groupby_type = 'date_type'
            elif rec.tele_chart_relation_sub_groupby.ttype == 'many2one':
                rec.tele_chart_sub_groupby_type = 'relational_type'

            elif rec.tele_chart_relation_sub_groupby.ttype == 'selection':
                rec.tele_chart_sub_groupby_type = 'selection'

            else:
                rec.tele_chart_sub_groupby_type = 'other'

    @api.depends('tele_chart_measure_field', 'tele_chart_cumulative_field', 'tele_chart_relation_groupby',
                 'tele_chart_date_groupby', 'tele_domain',
                 'tele_dashboard_item_type', 'tele_model_id', 'tele_sort_by_field', 'tele_sort_by_order',
                 'tele_record_data_limit', 'tele_chart_data_count_type', 'tele_chart_measure_field_2', 'tele_goal_enable',
                 'tele_standard_goal_value', 'tele_goal_bar_line', 'tele_chart_relation_sub_groupby',
                 'tele_chart_date_sub_groupby', 'tele_date_filter_field', 'tele_item_start_date', 'tele_item_end_date',
                 'tele_compare_period', 'tele_year_period', 'tele_unit', 'tele_unit_selection', 'tele_chart_unit',
                 'tele_fill_temporal', 'tele_domain_extension','tele_multiplier_active', 'tele_multiplier_lines',)
    def tele_get_chart_data(self):
        for rec in self:
            rec.tele_chart_data = rec._tele_get_chart_data(domain=[])

    def _tele_get_chart_data(self, domain=[]):
        rec = self
        if rec.tele_dashboard_item_type and rec.tele_dashboard_item_type != 'tele_tile' and \
                rec.tele_dashboard_item_type != 'tele_list_view' and rec.tele_model_id and rec.tele_chart_data_count_type:
            tele_chart_data = {'labels': [], 'datasets': [], 'tele_currency': 0, 'tele_field': "", 'tele_selection': "",
                             'tele_show_second_y_scale': False, 'domains': [], }
            tele_chart_measure_field = []
            tele_chart_measure_field_with_type = []
            tele_chart_measure_field_ids = []
            tele_chart_measure_field_2 = []
            tele_chart_measure_field_with_type_2 = []
            tele_chart_measure_field_2_ids = []

            if rec.tele_unit and rec.tele_unit_selection == 'monetary':
                tele_chart_data['tele_selection'] += rec.tele_unit_selection
                tele_chart_data['tele_currency'] += rec.env.user.company_id.currency_id.id
            elif rec.tele_unit and rec.tele_unit_selection == 'custom':
                tele_chart_data['tele_selection'] += rec.tele_unit_selection
                if rec.tele_chart_unit:
                    tele_chart_data['tele_field'] += rec.tele_chart_unit

            # If count chart data type:
            if rec.tele_chart_data_count_type == "count":
                rec.tele_chart_measure_field = False
                rec.tele_chart_measure_field_2 = False
                if not rec.tele_sort_by_field:
                    tele_chart_measure_field_with_type.append('count:count(id)')
                elif rec.tele_sort_by_field:
                    if not rec.tele_sort_by_field.ttype == "datetime":
                        tele_chart_measure_field_with_type.append(rec.tele_sort_by_field.name + ':' + 'sum')
                    else:
                        tele_chart_measure_field_with_type.append(rec.tele_sort_by_field.name)


                tele_chart_data['datasets'].append({'data': [], 'label': "Count"})
            else:
                if rec.tele_dashboard_item_type == 'tele_bar_chart':
                    if rec.tele_chart_measure_field_2:
                        tele_chart_data['tele_show_second_y_scale'] = True

                    for res in rec.tele_chart_measure_field_2:
                        if rec.tele_chart_data_count_type == 'sum':
                            tele_data_count_type = 'sum'
                        elif rec.tele_chart_data_count_type == 'average':
                            tele_data_count_type = 'avg'
                        else:
                            raise ValidationError(_('Please chose any Data Type!'))
                        tele_chart_measure_field_2.append(res.name)
                        tele_chart_measure_field_with_type_2.append(res.name + ':' + tele_data_count_type)
                        tele_chart_measure_field_2_ids.append(res.id)
                        tele_chart_data['datasets'].append(
                            {'data': [], 'label': res.field_description, 'type': 'line', 'yAxisID': 'y-axis-1'})

                for res in range(0, len(rec.tele_chart_measure_field)):
                    if rec.tele_chart_data_count_type == 'sum':
                        tele_data_count_type = 'sum'
                    elif rec.tele_chart_data_count_type == 'average':
                        tele_data_count_type = 'avg'
                    else:
                        raise ValidationError(_('Please chose any Data Type!'))
                    tele_chart_measure_field_with_type.append(
                        rec.tele_chart_measure_field[res].name + ':' + tele_data_count_type)
                    tele_chart_measure_field.append(rec.tele_chart_measure_field[res].name)
                    tele_chart_measure_field_ids.append(rec.tele_chart_measure_field[res].ids[0])

                    if len(rec.tele_chart_cumulative_field) > len(rec.tele_chart_measure_field):
                        rec.tele_chart_cumulative_field = rec.tele_chart_measure_field

                    if rec.tele_chart_cumulative_field and res < len(rec.tele_chart_cumulative_field)  and \
                            (rec.tele_chart_cumulative_field[res].id or rec.tele_chart_cumulative_field[res].id.origin) in rec.tele_chart_measure_field.ids:

                        tele_chart_data['datasets'].append(
                            {'data': [], 'label': rec.tele_chart_cumulative_field[res].field_description,
                             'tele_chart_cumulative_field': True})
                    else:
                        tele_chart_data['datasets'].append(
                            {'data': [], 'label': rec.tele_chart_measure_field[res].field_description,
                             'tele_chart_cumulative_field': False})

            # tele_chart_measure_field = [res.name for res in rec.tele_chart_measure_field]
            tele_chart_groupby_relation_field = rec.tele_chart_relation_groupby.name
            tele_chart_domain = self.tele_convert_into_proper_domain(rec.tele_domain, rec, domain)
            tele_chart_data['previous_domain'] = tele_chart_domain
            if rec.tele_chart_data_count_type == "count" and not self.tele_fill_temporal and not rec.tele_sort_by_field:
                orderby = 'count'
            else:
                orderby = rec.tele_sort_by_field.name if rec.tele_sort_by_field else "id"
            if rec.tele_sort_by_order:
                orderby = orderby + " " + rec.tele_sort_by_order
            limit = rec.tele_record_data_limit if rec.tele_record_data_limit and rec.tele_record_data_limit > 0 else 5000

            if ((rec.tele_chart_data_count_type != "count" and tele_chart_measure_field) or (
                    rec.tele_chart_data_count_type == "count" and not tele_chart_measure_field)) \
                    and not rec.tele_chart_relation_sub_groupby:
                if rec.tele_chart_relation_groupby.ttype == 'date' and rec.tele_chart_date_groupby in (
                        'minute', 'hour'):
                    raise ValidationError(_('Groupby field: {} cannot be aggregated by {}').format(
                        rec.tele_chart_relation_groupby.display_name, rec.tele_chart_date_groupby))
                    tele_chart_date_groupby = 'day'
                elif rec.tele_chart_date_groupby == 'month_year':
                    tele_chart_date_groupby = 'month'
                else:
                    tele_chart_date_groupby = rec.tele_chart_date_groupby

                if (rec.tele_chart_groupby_type == 'date_type' and rec.tele_chart_date_groupby) or \
                        rec.tele_chart_groupby_type != 'date_type':
                    tele_chart_data = rec.tele_fetch_chart_data(rec.tele_model_name, tele_chart_domain,
                                                            tele_chart_measure_field_with_type,
                                                            tele_chart_measure_field_with_type_2,
                                                            tele_chart_measure_field,
                                                            tele_chart_measure_field_2,
                                                            tele_chart_groupby_relation_field,
                                                            tele_chart_date_groupby,
                                                            rec.tele_chart_groupby_type, orderby, limit,
                                                            rec.tele_chart_data_count_type,
                                                            tele_chart_measure_field_ids,
                                                            tele_chart_measure_field_2_ids,
                                                            rec.tele_chart_relation_groupby.id, tele_chart_data)

                    if rec.tele_chart_groupby_type == 'date_type' and rec.tele_goal_enable and rec.tele_dashboard_item_type in [
                        'tele_bar_chart', 'tele_horizontalBar_chart', 'tele_line_chart',
                        'tele_area_chart'] and rec.tele_chart_groupby_type == "date_type":

                        if rec._context.get('current_id', False):
                            tele_item_id = rec._context['current_id']
                        else:
                            tele_item_id = rec.id

                        if rec.tele_date_filter_selection == "l_none":
                            selected_start_date = rec._context.get('teleDateFilterStartDate', False)
                            selected_end_date = rec._context.get('teleDateFilterEndDate', False)

                        else:
                            if rec.tele_date_filter_selection == "l_custom":
                                selected_start_date = rec.tele_item_start_date
                                selected_end_date = rec.tele_item_end_date
                            else:
                                tele_date_data = tele_get_date(rec.tele_date_filter_selection, self,
                                                           rec.tele_date_filter_field.ttype)
                                selected_start_date = tele_date_data["selected_start_date"]
                                selected_end_date = tele_date_data["selected_end_date"]

                        if selected_start_date and selected_end_date:
                            selected_start_date = selected_start_date.strftime('%Y-%m-%d')
                            selected_end_date = selected_end_date.strftime('%Y-%m-%d')
                        tele_goal_domain = [('tele_dashboard_item', '=', tele_item_id)]

                        if selected_start_date and selected_end_date:
                            tele_goal_domain.extend([('tele_goal_date', '>=', selected_start_date.split(" ")[0]),
                                                   ('tele_goal_date', '<=', selected_end_date.split(" ")[0])])

                        tele_date_data = rec.tele_get_start_end_date(rec.tele_model_name, tele_chart_groupby_relation_field,
                                                                 rec.tele_chart_relation_groupby.ttype,
                                                                 tele_chart_domain,
                                                                 tele_goal_domain)

                        labels = []
                        if rec.tele_chart_date_groupby == 'month_year':
                            tele_chart_date_groupby = 'month'
                        else:
                            tele_chart_date_groupby = rec.tele_chart_date_groupby
                        if tele_date_data['start_date'] and tele_date_data['end_date'] and rec.tele_goal_lines:
                            labels = self.generate_timeserise(tele_date_data['start_date'], tele_date_data['end_date'],
                                                              tele_chart_date_groupby)

                        tele_goal_records = self.env['tele_dashboard_ninja.item_goal'].read_group(
                            tele_goal_domain, ['tele_goal_value'],
                            ['tele_goal_date' + ":" + tele_chart_date_groupby], lazy=False)
                        tele_goal_labels = []
                        tele_goal_dataset = []
                        goal_dataset = []

                        if rec.tele_goal_lines and len(rec.tele_goal_lines) != 0:
                            tele_goal_domains = {}
                            for res in tele_goal_records:
                                if res['tele_goal_date' + ":" + tele_chart_date_groupby]:
                                    tele_goal_labels.append(res['tele_goal_date' + ":" + tele_chart_date_groupby])
                                    tele_goal_dataset.append(res['tele_goal_value'])
                                    tele_goal_domains[res['tele_goal_date' + ":" + tele_chart_date_groupby]] = res[
                                        '__domain']

                            for goal_domain in tele_goal_domains.keys():
                                tele_goal_doamins = []
                                for item in tele_goal_domains[goal_domain]:

                                    if 'tele_goal_date' in item:
                                        domain = list(item)
                                        domain[0] = tele_chart_groupby_relation_field
                                        domain = tuple(domain)
                                        tele_goal_doamins.append(domain)
                                tele_goal_doamins.insert(0, '&')
                                tele_goal_domains[goal_domain] = tele_goal_doamins

                            domains = {}
                            counter = 0
                            for label in tele_chart_data['labels']:
                                domains[label] = tele_chart_data['domains'][counter]
                                counter += 1

                            tele_chart_records_dates = tele_chart_data['labels'] + list(
                                set(tele_goal_labels) - set(tele_chart_data['labels']))

                            tele_chart_records = []
                            for label in labels:
                                if label in tele_chart_records_dates:
                                    tele_chart_records.append(label)

                            tele_chart_data['domains'].clear()
                            datasets = []
                            for dataset in tele_chart_data['datasets']:
                                datasets.append(dataset['data'].copy())

                            for dataset in tele_chart_data['datasets']:
                                dataset['data'].clear()

                            for label in tele_chart_records:
                                domain = domains.get(label, False)
                                if domain:
                                    tele_chart_data['domains'].append(domain)
                                else:
                                    tele_chart_data['domains'].append(tele_goal_domains.get(label, []))
                                counterr = 0
                                if label in tele_chart_data['labels']:
                                    index = tele_chart_data['labels'].index(label)

                                    for dataset in tele_chart_data['datasets']:
                                        dataset['data'].append(datasets[counterr][index])
                                        counterr += 1

                                else:
                                    for dataset in tele_chart_data['datasets']:
                                        dataset['data'].append(0.00)

                                if label in tele_goal_labels:
                                    index = tele_goal_labels.index(label)
                                    goal_dataset.append(tele_goal_dataset[index])
                                else:
                                    goal_dataset.append(0.00)

                            tele_chart_data['labels'] = tele_chart_records
                        else:
                            if rec.tele_standard_goal_value:
                                length = len(tele_chart_data['datasets'][0]['data'])
                                for i in range(length):
                                    goal_dataset.append(rec.tele_standard_goal_value)
                        tele_goal_datasets = {
                            'label': 'Target',
                            'data': goal_dataset,
                        }
                        if rec.tele_goal_bar_line:
                            tele_goal_datasets['type'] = 'line'
                            tele_chart_data['datasets'].insert(0, tele_goal_datasets)
                        else:
                            tele_chart_data['datasets'].append(tele_goal_datasets)

            elif rec.tele_chart_relation_sub_groupby and ((rec.tele_chart_sub_groupby_type == 'relational_type') or
                                                        (rec.tele_chart_sub_groupby_type == 'selection') or
                                                        (rec.tele_chart_sub_groupby_type == 'date_type' and
                                                         rec.tele_chart_date_sub_groupby) or
                                                        (rec.tele_chart_sub_groupby_type == 'other')):
                if rec.tele_chart_relation_sub_groupby.ttype == 'date':
                    if rec.tele_chart_date_sub_groupby in ('minute', 'hour'):
                        raise ValidationError(_('Sub Groupby field: {} cannot be aggregated by {}').format(
                            rec.tele_chart_relation_sub_groupby.display_name, rec.tele_chart_date_sub_groupby))
                    if rec.tele_chart_date_groupby in ('minute', 'hour'):
                        raise ValidationError(_('Groupby field: {} cannot be aggregated by {}').format(
                            rec.tele_chart_relation_sub_groupby.display_name, rec.tele_chart_date_groupby))
                    # doesn't have time in date
                    tele_chart_date_sub_groupby = rec.tele_chart_date_sub_groupby
                    tele_chart_date_groupby = rec.tele_chart_date_groupby
                else:
                    tele_chart_date_sub_groupby = rec.tele_chart_date_sub_groupby
                    if rec.tele_chart_date_groupby == 'month_year':
                        tele_chart_date_groupby = 'month'
                    else:
                        tele_chart_date_groupby = rec.tele_chart_date_groupby
                if len(tele_chart_measure_field) != 0 or rec.tele_chart_data_count_type == 'count':
                    if rec.tele_chart_groupby_type == 'date_type' and tele_chart_date_groupby:
                        tele_chart_group = rec.tele_chart_relation_groupby.name + ":" + tele_chart_date_groupby
                    else:
                        tele_chart_group = rec.tele_chart_relation_groupby.name

                    if rec.tele_chart_sub_groupby_type == 'date_type' and rec.tele_chart_date_sub_groupby:
                        tele_chart_sub_groupby_field = rec.tele_chart_relation_sub_groupby.name + ":" + \
                                                     tele_chart_date_sub_groupby
                    else:
                        tele_chart_sub_groupby_field = rec.tele_chart_relation_sub_groupby.name

                    tele_chart_groupby_relation_fields = [tele_chart_group, tele_chart_sub_groupby_field]
                    tele_chart_record = False
                    try:
                        tele_chart_record = self.env[rec.tele_model_name].read_group(tele_chart_domain,
                                                                                 list(set(
                                                                                     tele_chart_measure_field_with_type +
                                                                                     tele_chart_measure_field_with_type_2 +
                                                                                     [
                                                                                         tele_chart_groupby_relation_field,
                                                                                         rec.tele_chart_relation_sub_groupby.name])),
                                                                                 tele_chart_groupby_relation_fields,
                                                                                 orderby=orderby, limit=limit,
                                                                                 lazy=False)
                    except Exception:
                        tele_chart_record = {}
                    chart_data = []
                    chart_sub_data = []
                    for res in tele_chart_record:
                        domain = res.get('__domain', [])
                        if res.get(tele_chart_groupby_relation_fields[0], False):
                            if rec.tele_chart_groupby_type == 'date_type':
                                # x-axis modification
                                if rec.tele_chart_date_groupby == "day" \
                                        and rec.tele_chart_date_sub_groupby in ["quarter", "year"]:
                                    label = " ".join(res[tele_chart_groupby_relation_fields[0]].split(" ")[0:2])
                                elif rec.tele_chart_date_groupby in ["minute", "hour"] and \
                                        rec.tele_chart_date_sub_groupby in ["month", "week", "quarter", "year"]:
                                    label = " ".join(res[tele_chart_groupby_relation_fields[0]].split(" ")[0:3])
                                elif rec.tele_chart_date_groupby == 'month_year':
                                    label = res[tele_chart_groupby_relation_fields[0]]
                                else:
                                    label = res[tele_chart_groupby_relation_fields[0]].split(" ")[0]
                            elif rec.tele_chart_groupby_type == 'selection':
                                selection = res[tele_chart_groupby_relation_fields[0]]
                                label = dict(self.env[rec.tele_model_name].fields_get(
                                    allfields=[tele_chart_groupby_relation_fields[0]])
                                             [tele_chart_groupby_relation_fields[0]]['selection'])[selection]
                            elif rec.tele_chart_groupby_type == 'relational_type':
                                label = res[tele_chart_groupby_relation_fields[0]][1]._value
                            elif rec.tele_chart_groupby_type == 'other':
                                label = res[tele_chart_groupby_relation_fields[0]]

                            labels = []
                            value = []
                            value_2 = []
                            labels_2 = []
                            if rec.tele_chart_data_count_type != 'count':
                                for ress in rec.tele_chart_measure_field:
                                    if rec.tele_chart_sub_groupby_type == 'date_type':
                                        if res[tele_chart_groupby_relation_fields[1]] is not False:
                                            labels.append(res[tele_chart_groupby_relation_fields[1]].split(" ")[
                                                              0] + " " + ress.field_description)
                                        else:
                                            labels.append(str(res[tele_chart_groupby_relation_fields[1]]) + " " +
                                                          ress.field_description)
                                    elif rec.tele_chart_sub_groupby_type == 'selection':
                                        if res[tele_chart_groupby_relation_fields[1]] is not False:
                                            selection = res[tele_chart_groupby_relation_fields[1]]
                                            labels.append(dict(self.env[rec.tele_model_name].fields_get(
                                                allfields=[tele_chart_groupby_relation_fields[1]])
                                                               [tele_chart_groupby_relation_fields[1]]['selection'])[
                                                              selection]
                                                          + " " + ress.field_description)
                                        else:
                                            labels.append(str(res[tele_chart_groupby_relation_fields[1]]))
                                    elif rec.tele_chart_sub_groupby_type == 'relational_type':
                                        if res[tele_chart_groupby_relation_fields[1]] is not False:
                                            labels.append(res[tele_chart_groupby_relation_fields[1]][1]._value
                                                          + " " + ress.field_description)
                                        else:
                                            labels.append(str(res[tele_chart_groupby_relation_fields[1]])
                                                          + " " + ress.field_description)
                                    elif rec.tele_chart_sub_groupby_type == 'other':
                                        if res[tele_chart_groupby_relation_fields[1]] is not False:
                                            labels.append(str(res[tele_chart_groupby_relation_fields[1]])
                                                          + "\'s " + ress.field_description)
                                        else:
                                            labels.append(str(res[tele_chart_groupby_relation_fields[1]])
                                                          + " " + ress.field_description)

                                    value.append(res.get(
                                        ress.name, 0))

                                if rec.tele_chart_measure_field_2 and rec.tele_dashboard_item_type == 'tele_bar_chart':
                                    for ress in rec.tele_chart_measure_field_2:
                                        if rec.tele_chart_sub_groupby_type == 'date_type':
                                            if res[tele_chart_groupby_relation_fields[1]] is not False:
                                                labels_2.append(
                                                    res[tele_chart_groupby_relation_fields[1]].split(" ")[0] + " "
                                                    + ress.field_description)
                                            else:
                                                labels_2.append(str(res[tele_chart_groupby_relation_fields[1]]) +
                                                                " " + ress.field_description)
                                        elif rec.tele_chart_sub_groupby_type == 'selection':
                                            selection = res[tele_chart_groupby_relation_fields[1]]
                                            labels_2.append(dict(self.env[rec.tele_model_name].fields_get(
                                                allfields=[tele_chart_groupby_relation_fields[1]])
                                                                 [tele_chart_groupby_relation_fields[1]][
                                                                     'selection'])[
                                                                selection] + " " + ress.field_description)
                                        elif rec.tele_chart_sub_groupby_type == 'relational_type':
                                            if res[tele_chart_groupby_relation_fields[1]] is not False:
                                                labels_2.append(
                                                    res[tele_chart_groupby_relation_fields[1]][1]._value + " " +
                                                    ress.field_description)
                                            else:
                                                labels_2.append(str(res[tele_chart_groupby_relation_fields[1]]) +
                                                                " " + ress.field_description)
                                        elif rec.tele_chart_sub_groupby_type == 'other':
                                            labels_2.append(str(
                                                res[tele_chart_groupby_relation_fields[1]]) + " " +
                                                            ress.field_description)

                                        value_2.append(res.get(
                                            ress.name, 0))

                                    chart_sub_data.append({
                                        'value': value_2,
                                        'labels': label,
                                        'series': labels_2,
                                        'domain': domain,
                                    })
                            else:
                                if rec.tele_chart_sub_groupby_type == 'date_type':
                                    if res[tele_chart_groupby_relation_fields[1]] is not False:
                                        labels.append(res[tele_chart_groupby_relation_fields[1]].split(" ")[0])
                                    else:
                                        labels.append(str(res[tele_chart_groupby_relation_fields[1]]))
                                elif rec.tele_chart_sub_groupby_type == 'selection':
                                    selection = res[tele_chart_groupby_relation_fields[1]]
                                    labels.append(dict(self.env[rec.tele_model_name].fields_get(
                                        allfields=[tele_chart_groupby_relation_fields[1]])
                                                       [tele_chart_groupby_relation_fields[1]]['selection'])[
                                                      selection])
                                elif rec.tele_chart_sub_groupby_type == 'relational_type':
                                    if res[tele_chart_groupby_relation_fields[1]] is not False:
                                        labels.append(res[tele_chart_groupby_relation_fields[1]][1]._value)
                                    else:
                                        labels.append(str(res[tele_chart_groupby_relation_fields[1]]))
                                elif rec.tele_chart_sub_groupby_type == 'other':
                                    labels.append(res[tele_chart_groupby_relation_fields[1]])
                                value.append(res['__count'])

                            chart_data.append({
                                'value': value,
                                'labels': label,
                                'series': labels,
                                'domain': domain,
                            })

                    xlabels = []
                    series = []
                    values = {}
                    domains = {}
                    for data in chart_data:
                        label = data['labels']
                        serie = data['series']
                        domain = data['domain']

                        if (len(xlabels) == 0) or (label not in xlabels):
                            xlabels.append(label)

                        if (label not in domains):
                            domains[label] = domain
                        else:
                            domains[label].insert(0, '|')
                            domains[label] = domains[label] + domain

                        series = series + serie
                        value = data['value']
                        counter = 0
                        for seri in serie:
                            if seri not in values:
                                values[seri] = {}
                            if label in values[seri]:
                                values[seri][label] = values[seri][label] + value[counter]
                            else:
                                values[seri][label] = value[counter]
                            counter += 1

                    final_datasets = []
                    for serie in series:
                        if serie not in final_datasets:
                            final_datasets.append(serie)

                    tele_data = []
                    for dataset in final_datasets:
                        tele_dataset = {
                            'value': [],
                            'key': dataset
                        }
                        for label in xlabels:
                            tele_dataset['value'].append({
                                'domain': domains[label],
                                'x': label,
                                'y': values[dataset][label] if label in values[dataset] else 0
                            })
                        tele_data.append(tele_dataset)

                    if rec.tele_chart_relation_sub_groupby.name == rec.tele_chart_relation_groupby.name == rec.tele_sort_by_field.name:
                        tele_data = rec.tele_sort_sub_group_by_records(tele_data, rec.tele_chart_groupby_type,
                                                                   rec.tele_chart_date_groupby, rec.tele_sort_by_order,
                                                                   rec.tele_chart_date_sub_groupby)

                    tele_chart_data = {
                        'labels': [],
                        'datasets': [],
                        'domains': [],
                        'tele_selection': "",
                        'tele_currency': 0,
                        'tele_field': "",
                        'previous_domain': tele_chart_domain
                    }

                    if rec.tele_unit and rec.tele_unit_selection == 'monetary':
                        tele_chart_data['tele_selection'] += rec.tele_unit_selection
                        tele_chart_data['tele_currency'] += rec.env.user.company_id.currency_id.id
                    elif rec.tele_unit and rec.tele_unit_selection == 'custom':
                        tele_chart_data['tele_selection'] += rec.tele_unit_selection
                        if rec.tele_chart_unit:
                            tele_chart_data['tele_field'] += rec.tele_chart_unit

                    if len(tele_data) != 0:
                        for res in tele_data[0]['value']:
                            tele_chart_data['labels'].append(res['x'])
                            tele_chart_data['domains'].append(res['domain'])
                        if rec.tele_chart_measure_field_2 and rec.tele_dashboard_item_type == 'tele_bar_chart':
                            tele_chart_data['tele_show_second_y_scale'] = True
                            values_2 = {}
                            series_2 = []
                            for data in chart_sub_data:
                                label = data['labels']
                                serie = data['series']
                                series_2 = series_2 + serie
                                value = data['value']

                                counter = 0
                                for seri in serie:
                                    if seri not in values_2:
                                        values_2[seri] = {}
                                    if label in values_2[seri]:
                                        values_2[seri][label] = values_2[seri][label] + value[counter]
                                    else:
                                        values_2[seri][label] = value[counter]
                                    counter += 1
                            final_datasets_2 = []
                            for serie in series_2:
                                if serie not in final_datasets_2:
                                    final_datasets_2.append(serie)
                            tele_data_2 = []
                            for dataset in final_datasets_2:
                                tele_dataset = {
                                    'value': [],
                                    'key': dataset
                                }
                                for label in xlabels:
                                    tele_dataset['value'].append({
                                        'x': label,
                                        'y': values_2[dataset][label] if label in values_2[dataset] else 0
                                    })
                                tele_data_2.append(tele_dataset)

                            for tele_dat in tele_data_2:
                                dataset = {
                                    'label': tele_dat['key'],
                                    'data': [],
                                    'type': 'line',
                                    'yAxisID': 'y-axis-1'

                                }
                                for res in tele_dat['value']:
                                    dataset['data'].append(res['y'])

                                tele_chart_data['datasets'].append(dataset)
                        for tele_dat in tele_data:
                            dataset = {
                                'label': tele_dat['key'],
                                'data': []
                            }
                            for res in tele_dat['value']:
                                dataset['data'].append(res['y'])

                            tele_chart_data['datasets'].append(dataset)

                        if rec.tele_goal_enable and rec.tele_standard_goal_value and rec.tele_dashboard_item_type in [
                            'tele_bar_chart', 'tele_line_chart', 'tele_area_chart', 'tele_horizontalBar_chart']:
                            goal_dataset = []
                            length = len(tele_chart_data['datasets'][0]['data'])
                            for i in range(length):
                                goal_dataset.append(rec.tele_standard_goal_value)
                            tele_goal_datasets = {
                                'label': 'Target',
                                'data': goal_dataset,
                            }
                            if rec.tele_goal_bar_line and rec.tele_dashboard_item_type != 'tele_horizontalBar_chart':
                                tele_goal_datasets['type'] = 'line'
                                tele_chart_data['datasets'].insert(0, tele_goal_datasets)
                            else:
                                tele_chart_data['datasets'].append(tele_goal_datasets)
                else:
                    tele_chart_data = False
            if self.tele_multiplier_active:
                for tele_multiplier in self.tele_multiplier_lines:
                    for i in range(0, len(tele_chart_data['datasets'])):
                        if tele_multiplier.tele_multiplier_fields.field_description in tele_chart_data['datasets'][i][
                            'label']:
                            data_values = tele_chart_data['datasets'][i]['data']
                            data_values = list(map(lambda x: tele_multiplier.tele_multiplier_value * x, data_values))
                            tele_chart_data['datasets'][i]['data'] = data_values
            return json.dumps(tele_chart_data)
        else:
            return False

    @api.depends('tele_domain', 'tele_dashboard_item_type', 'tele_pagination_limit', 'tele_model_id', 'tele_sort_by_field',
                 'tele_sort_by_order', 'tele_multiplier_active', 'tele_multiplier_lines',
                 'tele_record_data_limit', 'tele_list_view_fields', 'tele_list_view_type', 'tele_list_view_group_fields',
                 'tele_chart_groupby_type', 'tele_chart_date_groupby', 'tele_date_filter_field', 'tele_item_end_date',
                 'tele_item_start_date', 'tele_compare_period', 'tele_year_period', 'tele_list_target_deviation_field',
                 'tele_goal_enable', 'tele_standard_goal_value', 'tele_goal_lines', 'tele_domain_extension')
    def tele_get_list_view_data(self):
        for rec in self:
            rec.tele_list_view_data = rec._teleGetListViewData(domain=[])

    def _teleGetListViewData(self, domain=[]):
        rec = self
        if rec.tele_list_view_type and rec.tele_dashboard_item_type and rec.tele_dashboard_item_type == 'tele_list_view' \
                and rec.tele_model_id:
            orderby = rec.tele_sort_by_field.id
            sort_order = rec.tele_sort_by_order
            tele_chart_domain = self.tele_convert_into_proper_domain(rec.tele_domain, rec, domain)
            tele_list_view_data = rec.get_list_view_record(orderby, sort_order, tele_chart_domain)
            if tele_list_view_data and len(tele_list_view_data) > 0:
                tele_list_view_data = json.dumps(tele_list_view_data)
            else:
                tele_list_view_data = False
        else:
            tele_list_view_data = False
        return tele_list_view_data

    def get_list_view_record(self, orderid, sort_order, tele_chart_domain, teleoffset=0,
                             initial_count=0, tele_export_all=False):
        tele_list_view_data = {'label': [], 'fields': [], 'fields_type': [],
                             'store': [], 'type': self.tele_list_view_type,
                             'data_rows': [], 'model': self.tele_model_name}
        tele_limit = self.tele_record_data_limit if self.tele_record_data_limit and self.tele_record_data_limit > 0 else False
        limit = self.tele_pagination_limit

        if tele_limit:
            tele_limit = tele_limit - teleoffset
            if tele_limit and tele_limit < self.tele_pagination_limit:
                limit = tele_limit
            else:
                limit = self.tele_pagination_limit
        if tele_export_all:
            limit = tele_limit
            offset = 0
        self.tele_sort_by_field = orderid
        self.tele_sort_by_order = sort_order
        orderby = self.tele_sort_by_field.name if self.tele_sort_by_field else "id"
        if self.tele_sort_by_order:
            orderby = orderby + " " + self.tele_sort_by_order
        if self.tele_list_view_type == "ungrouped":
            if self.tele_list_view_fields:
                tele_list_view_data = self.tele_fetch_list_view_data(self, tele_chart_domain, offset=teleoffset,
                                                                 initial_count=initial_count)
        elif self.tele_list_view_type == "grouped" and self.tele_list_view_group_fields \
                and self.tele_chart_relation_groupby:
            tele_list_fields = []

            if self.tele_chart_groupby_type == 'relational_type':
                tele_list_view_data['list_view_type'] = 'relational_type'
                tele_list_view_data['groupby'] = self.tele_chart_relation_groupby.name
                tele_list_fields.append(self.tele_chart_relation_groupby.name)
                tele_list_view_data['fields'].append(self.tele_chart_relation_groupby.ids[0])
                tele_list_view_data['fields_type'].append(self.tele_chart_relation_groupby.ttype)
                tele_list_view_data['store'].append(self.tele_chart_relation_groupby.store)
                tele_list_view_data['label'].append(self.tele_chart_relation_groupby.field_description)
                for res in self.tele_list_view_group_fields:
                    tele_list_fields.append(res.name)
                    tele_list_view_data['label'].append(res.field_description)
                    tele_list_view_data['fields'].append(res.ids[0])
                    tele_list_view_data['fields_type'].append(res.ttype)
                    tele_list_view_data['store'].append(res.store)

                try:
                    tele_list_view_records = self.env[self.tele_model_name]. \
                    read_group(tele_chart_domain, tele_list_fields, [self.tele_chart_relation_groupby.name],
                               orderby=orderby, limit=limit, offset=teleoffset, lazy=False)
                except Exception as e:
                    tele_list_view_records = []
                for res in tele_list_view_records:
                    if all(list_fields in res for list_fields in tele_list_fields) \
                            and res[self.tele_chart_relation_groupby.name]:
                        counter = 0
                        data_row = {'id': res[self.tele_chart_relation_groupby.name][0], 'data': [],
                                    'domain': json.dumps(res['__domain']), 'tele_column_type': []}
                        for field_rec in tele_list_fields:
                            if counter == 0:
                                data_row['data'].append(res[field_rec][1]._value)
                            else:
                                data_row['data'].append(res[field_rec])
                            counter += 1
                            data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                        tele_list_view_data['data_rows'].append(data_row)

            elif self.tele_chart_groupby_type == 'date_type' and self.tele_chart_date_groupby:
                tele_list_view_data['list_view_type'] = 'date_type'
                tele_list_field = []
                tele_chart_date_groupby = self.tele_chart_date_groupby
                if self.tele_chart_date_groupby == 'month_year':
                    tele_chart_date_groupby = 'month'
                tele_list_view_data[
                    'groupby'] = self.tele_chart_relation_groupby.name + ':' + tele_chart_date_groupby
                tele_list_field.append(self.tele_chart_relation_groupby.name)
                tele_list_fields.append(self.tele_chart_relation_groupby.name + ':' + tele_chart_date_groupby)
                tele_list_view_data['label'].append(
                    self.tele_chart_relation_groupby.field_description + ' : ' + tele_chart_date_groupby
                    .capitalize())
                tele_list_view_data['fields'].append(self.tele_chart_relation_groupby.ids[0])
                tele_list_view_data['fields_type'].append(self.tele_chart_relation_groupby.ttype)
                tele_list_view_data['store'].append(self.tele_chart_relation_groupby.store)
                for res in self.tele_list_view_group_fields:
                    tele_list_fields.append(res.name)
                    tele_list_field.append(res.name)
                    tele_list_view_data['label'].append(res.field_description)
                    tele_list_view_data['fields'].append(res.ids[0])
                    tele_list_view_data['fields_type'].append(res.ttype)
                    tele_list_view_data['store'].append(res.store)
                tele_label = tele_list_view_data['label'].copy()
                tele_fields = tele_list_view_data['fields'].copy()
                tele_fields_type = tele_list_view_data['fields_type'].copy()

                list_target_deviation_field = []
                if self.tele_goal_enable and self.tele_list_target_deviation_field:
                    list_target_deviation_field.append(self.tele_list_target_deviation_field.name)
                    if self.tele_list_target_deviation_field.name in tele_list_field:
                        tele_list_field.remove(self.tele_list_target_deviation_field.name)
                        tele_list_fields.remove(self.tele_list_target_deviation_field.name)
                        tele_list_view_data['label'].remove(self.tele_list_target_deviation_field.field_description)
                try:
                    tele_list_view_records = self.env[self.tele_model_name]. \
                    read_group(tele_chart_domain, tele_list_field + list_target_deviation_field,
                               [self.tele_chart_relation_groupby.name + ':' + tele_chart_date_groupby],
                               orderby=orderby, limit=limit, offset=teleoffset, lazy=False)
                except Exception as E:
                    tele_list_view_records = []
                if all(list_fields in res for res in tele_list_view_records for list_fields in
                       tele_list_fields + list_target_deviation_field):
                    for res in tele_list_view_records:
                        counter = 0
                        data_row = {'id': 0, 'data': [], 'domain': json.dumps(res['__domain']), 'tele_column_type': []}
                        for field_rec in tele_list_fields:
                            data_row['data'].append(res[field_rec])
                            data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                        tele_list_view_data['data_rows'].append(data_row)

                    if self.tele_goal_enable:
                        tele_list_labels = []
                        tele_list_view_data['label'].append("Target")

                        if self.tele_list_target_deviation_field:
                            tele_list_view_data['label'].append(
                                self.tele_list_target_deviation_field.field_description)
                            tele_list_view_data['label'].append("Achievement")
                            tele_list_view_data['label'].append("Deviation")

                        for res in tele_list_view_records:
                            tele_list_labels.append(res[tele_list_view_data['groupby']])
                        tele_list_view_data2 = self.get_target_list_view_data(tele_list_view_records, self,
                                                                            tele_list_fields,
                                                                            tele_list_view_data['groupby'],
                                                                            list_target_deviation_field,
                                                                            tele_chart_domain)
                        tele_list_view_data['data_rows'] = tele_list_view_data2['data_rows']
                        tele_list_view_data['store'].clear()
                        tele_list_view_data['fields_type'].clear()
                        tele_list_view_data['fields'].clear()
                        for label in tele_list_view_data['label']:
                            if label == 'Achievement':
                                tele_list_view_data['store'].append(False)
                                tele_list_view_data['fields_type'].append(False)
                                tele_list_view_data['fields'].append(False)
                            elif label == 'Target':
                                tele_list_view_data['store'].append(False)
                                tele_list_view_data['fields_type'].append(False)
                                tele_list_view_data['fields'].append(False)
                            elif label == 'Deviation':
                                tele_list_view_data['store'].append(False)
                                tele_list_view_data['fields_type'].append(False)
                                tele_list_view_data['fields'].append(False)
                            else:
                                tele_list_view_data['store'].append(True)
                                if label in tele_label:
                                    index = tele_label.index(label)
                                    tele_fields_value = tele_fields[index]
                                    tele_fields_type_value = tele_fields_type[index]
                                    tele_list_view_data['fields_type'].append(tele_fields_type_value)
                                    tele_list_view_data['fields'].append(tele_fields_value)



            elif self.tele_chart_groupby_type == 'selection':
                tele_list_view_data['list_view_type'] = 'selection'
                tele_list_view_data['groupby'] = self.tele_chart_relation_groupby.name
                tele_list_view_data['fields'].append(self.tele_chart_relation_groupby.ids[0])
                tele_list_view_data['fields_type'].append(self.tele_chart_relation_groupby.ttype)
                tele_list_view_data['store'].append(self.tele_chart_relation_groupby.store)
                tele_selection_field = self.tele_chart_relation_groupby.name
                tele_list_view_data['label'].append(self.tele_chart_relation_groupby.field_description)
                for res in self.tele_list_view_group_fields:
                    tele_list_fields.append(res.name)
                    tele_list_view_data['label'].append(res.field_description)
                    tele_list_view_data['fields'].append(res.ids[0])
                    tele_list_view_data['fields_type'].append(res.ttype)
                    tele_list_view_data['store'].append(res.store)

                try:
                    tele_list_view_records = self.env[self.tele_model_name] \
                    .read_group(tele_chart_domain, tele_list_fields, [self.tele_chart_relation_groupby.name],
                                orderby=orderby, limit=limit, offset=teleoffset, lazy=False)
                except Exception as e:
                    tele_list_view_records = []
                for res in tele_list_view_records:
                    if all(list_fields in res for list_fields in tele_list_fields):
                        counter = 0
                        data_row = {'id': 0, 'data': [], 'domain': json.dumps(res['__domain']), 'tele_column_type': []}
                        if res[tele_selection_field]:
                            data_row['data'].append(dict(
                                self.env[self.tele_model_name].fields_get(allfields=tele_selection_field)
                                [tele_selection_field]['selection'])[res[tele_selection_field]])
                        else:
                            data_row['data'].append(" ")
                        data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                        for field_rec in tele_list_fields:
                            data_row['data'].append(res[field_rec])
                            data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                        tele_list_view_data['data_rows'].append(data_row)

            elif self.tele_chart_groupby_type == 'other':
                tele_list_view_data['list_view_type'] = 'other'
                tele_list_view_data['groupby'] = self.tele_chart_relation_groupby.name
                tele_list_fields.append(self.tele_chart_relation_groupby.name)
                tele_list_view_data['fields'].append(self.tele_chart_relation_groupby.ids[0])
                tele_list_view_data['fields_type'].append(self.tele_chart_relation_groupby.ttype)
                tele_list_view_data['store'].append(self.tele_chart_relation_groupby.store)
                tele_list_view_data['label'].append(self.tele_chart_relation_groupby.field_description)
                for res in self.tele_list_view_group_fields:
                    if res.name != self.tele_chart_relation_groupby.name:
                        tele_list_fields.append(res.name)
                        tele_list_view_data['label'].append(res.field_description)
                        tele_list_view_data['fields'].append(res.ids[0])
                        tele_list_view_data['fields_type'].append(res.ttype)
                        tele_list_view_data['store'].append(res.store)

                try:
                    tele_list_view_records = self.env[self.tele_model_name] \
                    .read_group(tele_chart_domain, tele_list_fields, [self.tele_chart_relation_groupby.name],
                                orderby=orderby, limit=limit, offset=teleoffset, lazy=False)
                except Exception as E:
                    tele_list_view_records = []
                for res in tele_list_view_records:
                    if all(list_fields in res for list_fields in tele_list_fields):
                        counter = 0
                        data_row = {'id': 0, 'data': [], 'domain': json.dumps(res['__domain']), 'tele_column_type': []}

                        for field_rec in tele_list_fields:
                            if counter == 0:
                                data_row['data'].append(res[field_rec])
                            else:
                                if self.tele_chart_relation_groupby.name == field_rec:
                                    data_row['data'].append(res[field_rec] * res[field_rec + '_count'])
                                else:
                                    data_row['data'].append(res[field_rec])
                            counter += 1
                            data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                        tele_list_view_data['data_rows'].append(data_row)

        # tele_list_view_data = json.dumps(tele_list_view_data)
        if self.tele_multiplier_active and self.tele_list_view_type == 'grouped':
            for tele_multiplier in self.tele_multiplier_lines:
                label = tele_multiplier.tele_multiplier_fields.field_description
                if label in tele_list_view_data['label']:
                    index = tele_list_view_data['label'].index(label)
                    for i in range(0, len(tele_list_view_data['data_rows'])):
                        data_values = tele_list_view_data['data_rows'][i]['data'][index] * tele_multiplier.tele_multiplier_value
                        tele_list_view_data['data_rows'][i]['data'][index] = data_values
        return tele_list_view_data

    def get_target_list_view_data(self, tele_list_view_records, rec, tele_list_fields, tele_group_by,
                                  target_deviation_field, tele_chart_domain):
        tele_list_view_data = {}
        tele_list_labels = []
        tele_list_records = {}
        tele_domains = {}
        for res in tele_list_view_records:
            tele_list_labels.append(res[tele_group_by])
            tele_domains[res[tele_group_by]] = res['__domain']
            tele_list_records[res[tele_group_by]] = {'measure_field': [], 'deviation_value': 0.0}
            tele_list_records[res[tele_group_by]]['measure_field'] = []
            for fields in tele_list_fields[1:]:
                tele_list_records[res[tele_group_by]]['measure_field'].append(res[fields])
            for field in target_deviation_field:
                tele_list_records[res[tele_group_by]]['deviation'] = res[field]

        if rec._context.get('current_id', False):
            tele_item_id = rec._context['current_id']
        else:
            tele_item_id = rec.id

        if rec.tele_date_filter_selection_2 == "l_none":
            selected_start_date = rec._context.get('teleDateFilterStartDate', False)
            selected_end_date = rec._context.get('teleDateFilterEndDate', False)
        else:
            selected_start_date = rec.tele_item_start_date
            selected_end_date = rec.tele_item_end_date

        tele_goal_domain = [('tele_dashboard_item', '=', tele_item_id)]

        if selected_start_date and selected_end_date:
            tele_goal_domain.extend([('tele_goal_date', '>=', selected_start_date.strftime("%Y-%m-%d")),
                                   ('tele_goal_date', '<=', selected_end_date.strftime("%Y-%m-%d"))])

        tele_date_data = rec.tele_get_start_end_date(rec.tele_model_name, rec.tele_chart_relation_groupby.name,
                                                 rec.tele_chart_relation_groupby.ttype,
                                                 tele_chart_domain,
                                                 tele_goal_domain)

        labels = []
        tele_chart_date_groupby = rec.tele_chart_date_groupby
        if rec.tele_chart_date_groupby == 'month_year':
            tele_chart_date_groupby = 'month'
        if tele_date_data['start_date'] and tele_date_data['end_date'] and rec.tele_goal_lines:
            labels = self.generate_timeserise(tele_date_data['start_date'], tele_date_data['end_date'],
                                              tele_chart_date_groupby)
        tele_goal_records = self.env['tele_dashboard_ninja.item_goal'].read_group(
            tele_goal_domain, ['tele_goal_value'],
            ['tele_goal_date' + ":" + tele_chart_date_groupby], lazy=False)

        tele_goal_labels = []
        tele_goal_dataset = {}
        tele_list_view_data['data_rows'] = []
        if rec.tele_goal_lines and len(rec.tele_goal_lines) != 0:
            tele_goal_domains = {}
            for res in tele_goal_records:
                if res['tele_goal_date' + ":" + tele_chart_date_groupby]:
                    tele_goal_labels.append(res['tele_goal_date' + ":" + tele_chart_date_groupby])
                    tele_goal_dataset[res['tele_goal_date' + ":" + tele_chart_date_groupby]] = res['tele_goal_value']
                    tele_goal_domains[res['tele_goal_date' + ":" + tele_chart_date_groupby]] = res.get('__domain')

            for goal_domain in tele_goal_domains.keys():
                tele_goal_doamins = []
                for item in tele_goal_domains[goal_domain]:

                    if 'tele_goal_date' in item:
                        domain = list(item)
                        domain[0] = tele_group_by.split(":")[0]
                        domain = tuple(domain)
                        tele_goal_doamins.append(domain)
                tele_goal_doamins.insert(0, '&')
                tele_goal_domains[goal_domain] = tele_goal_doamins

            tele_chart_records_dates = tele_list_labels + list(
                set(tele_goal_labels) - set(tele_list_labels))

            tele_list_labels_dates = []
            for label in labels:
                if label in tele_chart_records_dates:
                    tele_list_labels_dates.append(label)

            for label in tele_list_labels_dates:
                data_rows = {'data': [label], 'tele_column_type': [],'store':True}
                data = tele_list_records.get(label, False)
                if data:
                    data_rows['data'] = data_rows['data'] + data['measure_field']
                    data_rows['domain'] = json.dumps(tele_domains[label])
                else:
                    for fields in tele_list_fields[1:]:
                        data_rows['data'].append(0.0)
                    data_rows['domain'] = json.dumps(tele_goal_domains[label])

                target_value = (tele_goal_dataset.get(label, 0.0))
                data_rows['data'].append(target_value)

                for field in target_deviation_field:
                    tele_multiplier = 1
                    if self.tele_multiplier_active:
                        for line in self.tele_multiplier_lines:
                            if line.tele_multiplier_fields.name == field:
                                tele_multiplier = line.tele_multiplier_value
                    if data:
                        data_rows['data'].append(data['deviation'])
                        value = data['deviation'] * tele_multiplier
                    else:
                        data_rows['data'].append(0.0)
                        value = 0
                    if target_value:
                        acheivement = round(((value) / target_value) * 100)
                        acheivement = str(acheivement) + "%"
                    else:
                        acheivement = ""
                    deviation = (value - target_value)

                    data_rows['data'].append(acheivement)
                    data_rows['data'].append(deviation)
                data_rows['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                tele_list_view_data['data_rows'].append(data_rows)

        else:
            for res in tele_list_view_records:
                if all(list_fields in res for list_fields in tele_list_fields):
                    counter = 0
                    data_row = {'id': 0, 'data': [], 'domain': json.dumps(res['__domain']), 'tele_column_type': [],'store':True}
                    for field_rec in tele_list_fields:
                        data_row['data'].append(res[field_rec])
                    data_row['data'].append(rec.tele_standard_goal_value)
                    data_row['domain'] = json.dumps(res['__domain'])
                    for field in target_deviation_field:
                        tele_multiplier = 1
                        if self.tele_multiplier_active:
                            for line in self.tele_multiplier_lines:
                                if line.tele_multiplier_fields.name == field:
                                    tele_multiplier = line.tele_multiplier_value

                        value = res[field] * tele_multiplier
                        data_row['data'].append(res[field])
                        target_value = rec.tele_standard_goal_value

                        if target_value:
                            acheivement = round(((value) / target_value) * 100)
                            acheivement = str(acheivement) + "%"
                        else:
                            acheivement = ""

                        deviation = (value - target_value)
                        data_row['data'].append(acheivement)
                        data_row['data'].append(deviation)
                    tele_list_view_data['data_rows'].append(data_row)

        return tele_list_view_data

    @api.model
    def tele_fetch_list_view_data(self, rec, tele_chart_domain, limit=15, offset=0, tele_export_all=False, initial_count=0):
        tele_list_view_data = {'label': [], 'fields': [], 'fields_type': [],
                             'store': [], 'type': 'ungrouped',
                             'data_rows': [], 'model': self.tele_model_name}

        # tele_chart_domain = self.tele_convert_into_proper_domain(self.tele_domain, self)
        orderby = self.tele_sort_by_field.name if self.tele_sort_by_field else "id"
        if self.tele_sort_by_order:
            orderby = orderby + " " + self.tele_sort_by_order

        tele_limit = self.tele_record_data_limit if self.tele_record_data_limit and self.tele_record_data_limit > 0 else False
        limit = self.tele_pagination_limit
        if tele_limit:
            tele_limit = tele_limit - offset
            if tele_limit and tele_limit < self.tele_pagination_limit:
                limit = tele_limit
            else:
                limit = self.tele_pagination_limit
        if tele_export_all:
            limit = tele_limit
            offset = 0
        if self.tele_list_view_fields:
            tele_list_view_data['list_view_type'] = 'other'
            tele_list_view_data['groupby'] = False
            tele_list_view_data['label'] = []
            tele_list_view_data['date_index'] = []
            for res in self.tele_list_view_fields:
                if (res.ttype == "datetime" or res.ttype == "date"):
                    index = len(tele_list_view_data['label'])
                    tele_list_view_data['label'].append(res.field_description)
                    tele_list_view_data['fields'].append(res.ids[0])
                    tele_list_view_data['date_index'].append(index)
                    tele_list_view_data['fields_type'].append(res.ttype)
                    tele_list_view_data['store'].append(res.store)
                else:
                    tele_list_view_data['label'].append(res.field_description)
                    tele_list_view_data['fields'].append(res.ids[0])
                    tele_list_view_data['fields_type'].append(res.ttype)
                    tele_list_view_data['store'].append(res.store)

            tele_list_view_fields = [res.name for res in self.tele_list_view_fields]
            tele_list_view_field_type = [res.ttype for res in self.tele_list_view_fields]
        try:
            tele_list_view_records = self.env[self.tele_model_name].search_read(tele_chart_domain,
                                                                            tele_list_view_fields,
                                                                            order=orderby, limit=limit, offset=offset)
        except Exception as e:
            tele_list_view_data = False
            return tele_list_view_data
        for res in tele_list_view_records:
            counter = 0
            data_row = {'id': res['id'], 'data': [], 'tele_column_type': []}
            for field_rec in tele_list_view_fields:
                if type(res[field_rec]) == fields.datetime or type(res[field_rec]) == fields.date:
                    res[field_rec] = res[field_rec].strftime("%D %T")
                elif tele_list_view_field_type[counter] == "many2one":
                    if res[field_rec]:
                        res[field_rec] = res[field_rec][1]
                elif tele_list_view_field_type[counter] == "selection" and res.get(field_rec, False):
                    res[field_rec] = dict(self.env[rec.tele_model_name].fields_get(allfields=[field_rec])
                                          [field_rec]['selection'])[res[field_rec]]
                data_row['data'].append(res[field_rec])
                data_row['tele_column_type'].append(tele_list_view_field_type[counter])
                counter += 1
            tele_list_view_data['data_rows'].append(data_row)

        return tele_list_view_data

    @api.onchange('tele_dashboard_item_type')
    def set_color_palette(self):
        for rec in self:
            if rec.tele_dashboard_item_type == "tele_bar_chart" or rec.tele_dashboard_item_type == "tele_horizontalBar_chart" \
                    or rec.tele_dashboard_item_type == "tele_line_chart" or rec.tele_dashboard_item_type == "tele_area_chart":
                rec.tele_chart_item_color = "cool"
            else:
                rec.tele_chart_item_color = "default"
            if rec.tele_dashboard_item_type == 'tele_kpi' or rec.tele_dashboard_item_type == 'tele_tile':
                rec.tele_data_calculation_type = 'custom'
            if rec.tele_dashboard_item_type != "tele_bar_chart":
                rec.tele_chart_cumulative_field = False
                rec.tele_chart_cumulative = False
            rec.tele_multiplier_active = False
            rec.tele_model_id_2 = False
            rec.tele_chart_measure_field_2 = False
            if rec.tele_dashboard_item_type == 'tele_to_do':
                rec.tele_model_id_2 = False
                rec.tele_model_id = False

    #  Time Filter Calculation

    @api.onchange('tele_date_filter_selection')
    def tele_set_date_filter(self):
        for rec in self:
            if (not rec.tele_date_filter_selection) or rec.tele_date_filter_selection == "l_none":
                rec.tele_item_start_date = rec.tele_item_end_date = False
            elif rec.tele_date_filter_selection != 'l_custom':
                tele_date_data = tele_get_date(rec.tele_date_filter_selection, self, rec.tele_date_filter_field.ttype)
                rec.tele_item_start_date = tele_date_data["selected_start_date"]
                rec.tele_item_end_date = tele_date_data["selected_end_date"]

    @api.depends('tele_dashboard_item_type', 'tele_goal_enable', 'tele_standard_goal_value', 'tele_record_count',
                 'tele_record_count_2', 'tele_previous_period', 'tele_compare_period', 'tele_year_period',
                 'tele_compare_period_2', 'tele_year_period_2', 'tele_domain_extension_2')
    def tele_get_kpi_data(self):
        for rec in self:
            rec.tele_kpi_data = rec._teleGetKpiData(domain1=[], domain2=[])

    def _teleGetKpiData(self, domain1=[], domain2=[]):
        rec = self
        if rec.tele_dashboard_item_type and rec.tele_dashboard_item_type == 'tele_kpi' and rec.tele_model_id:
            tele_kpi_data = []
            tele_record_count = 0.0
            tele_kpi_data_model_1 = {}
            tele_record_count = rec._teleGetRecordCount(domain1)
            tele_kpi_data_model_1['model'] = rec.tele_model_name
            tele_kpi_data_model_1['record_field'] = rec.tele_record_field.field_description
            tele_kpi_data_model_1['record_data'] = tele_record_count

            if rec.tele_goal_enable:
                tele_kpi_data_model_1['target'] = rec.tele_standard_goal_value
            tele_kpi_data.append(tele_kpi_data_model_1)

            if rec.tele_previous_period:
                tele_previous_period_data = rec.tele_get_previous_period_data(rec)
                tele_kpi_data_model_1['previous_period'] = tele_previous_period_data

            if rec.tele_model_id_2 and rec.tele_record_count_type_2:
                tele_kpi_data_model_2 = {}
                tele_kpi_data_model_2['model'] = rec.tele_model_name_2
                tele_kpi_data_model_2[
                    'record_field'] = 'count' if rec.tele_record_count_type_2 == 'count' else \
                    rec.tele_record_field_2.field_description
                tele_kpi_data_model_2['record_data'] = rec._teleGetRecordCount_2(domain2)
                tele_kpi_data.append(tele_kpi_data_model_2)

            return json.dumps(tele_kpi_data)
        else:
            return False

    # writing separate function for fetching previous period data
    def tele_get_previous_period_data(self, rec):
        switcher = {
            'l_day': 'ls_day',
            't_week': 'ls_week',
            't_month': 'ls_month',
            't_quarter': 'ls_quarter',
            't_year': 'ls_year',
        }
        tele_previous_period = False
        tele_date_data = False
        if rec.tele_date_filter_selection == "l_none":
            date_filter_selection = rec.tele_dashboard_ninja_board_id.tele_date_filter_selection
        else:
            date_filter_selection = rec.tele_date_filter_selection
            tele_previous_period = switcher.get(date_filter_selection, False)
        if tele_previous_period:
            tele_date_data = tele_get_date(tele_previous_period, self, rec.tele_date_filter_field.ttype)

        if (tele_date_data):
            previous_period_start_date = tele_date_data["selected_start_date"]
            previous_period_end_date = tele_date_data["selected_end_date"]
            proper_domain = rec.tele_get_previous_period_domain(rec.tele_domain, previous_period_start_date,
                                                              previous_period_end_date, rec.tele_date_filter_field)
            tele_record_count = 0.0

            if rec.tele_record_count_type == 'count':
                tele_record_count = 0
                try:
                    tele_record_count = self.env[rec.tele_model_name].search_count(proper_domain)
                except Exception as E:
                    tele_record_count = 0
                return tele_record_count

            elif rec.tele_record_field:
                try:
                    data = \
                        self.env[rec.tele_model_name].read_group(proper_domain, [rec.tele_record_field.name], [], lazy=False)[0]
                except Exception as E:
                    data = {}
                if rec.tele_record_count_type == 'sum':
                    return data.get(rec.tele_record_field.name, 0) if data.get('__count', False) and (
                        data.get(rec.tele_record_field.name)) else 0
                else:
                    return data.get(rec.tele_record_field.name, 0) / data.get('__count', 1) \
                        if data.get('__count', False) and (data.get(rec.tele_record_field.name)) else 0
            else:
                return False
        else:
            return False

    def tele_get_previous_period_domain(self, tele_domain, tele_start_date, tele_end_date, date_filter_field):
        if tele_domain and "%UID" in tele_domain:
            tele_domain = tele_domain.replace('"%UID"', str(self.env.user.id))
        if tele_domain:
            # try:
            proper_domain = safe_eval(tele_domain)
            if tele_start_date and tele_end_date and date_filter_field:
                proper_domain.extend([(date_filter_field.name, ">=", tele_start_date),
                                      (date_filter_field.name, "<=", tele_end_date)])

        else:
            if tele_start_date and tele_end_date and date_filter_field:
                proper_domain = ([(date_filter_field.name, ">=", tele_start_date),
                                  (date_filter_field.name, "<=", tele_end_date)])
            else:
                proper_domain = []
        return proper_domain

    @api.depends('tele_domain_2', 'tele_model_id_2', 'tele_record_field_2', 'tele_record_count_type_2', 'tele_item_start_date_2',
                 'tele_date_filter_selection_2', 'tele_record_count_type_2', 'tele_compare_period_2', 'tele_year_period_2')
    def tele_get_record_count_2(self):
        for rec in self:
            rec.tele_record_count_2 = rec._teleGetRecordCount_2(domain=[])

    def _teleGetRecordCount_2(self, domain=[]):
        rec = self
        if rec.tele_record_count_type_2 == 'count':
            tele_record_count = rec.tele_fetch_model_data_2(rec.tele_model_name_2, rec.tele_domain_2, 'search_count', rec,
                                                        domain)

        elif rec.tele_record_count_type_2 in ['sum', 'average'] and rec.tele_record_field_2:
            tele_records_grouped_data = rec.tele_fetch_model_data_2(rec.tele_model_name_2, rec.tele_domain_2, 'read_group',
                                                                rec, domain)
            if tele_records_grouped_data and len(tele_records_grouped_data) > 0:
                tele_records_grouped_data = tele_records_grouped_data[0]
                if rec.tele_record_count_type_2 == 'sum' and tele_records_grouped_data.get('__count', False) and (
                        tele_records_grouped_data.get(rec.tele_record_field_2.name)):
                    tele_record_count = tele_records_grouped_data.get(rec.tele_record_field_2.name, 0)
                elif rec.tele_record_count_type_2 == 'average' and tele_records_grouped_data.get(
                        '__count', False) and (tele_records_grouped_data.get(rec.tele_record_field_2.name)):
                    tele_record_count = tele_records_grouped_data.get(rec.tele_record_field_2.name,
                                                                  0) / tele_records_grouped_data.get('__count',
                                                                                                   1)
                else:
                    tele_record_count = 0
            else:
                tele_record_count = 0
        else:
            tele_record_count = False

        return tele_record_count

    @api.onchange('tele_model_id_2')
    def make_record_field_empty_2(self):
        for rec in self:
            rec.tele_record_field_2 = False
            rec.tele_domain_2 = False
            rec.tele_date_filter_field_2 = False
            # To show "created on" by default on date filter field on model select.
            if rec.tele_model_id:
                datetime_field_list = rec.tele_date_filter_field_2.search(
                    [('model_id', '=', rec.tele_model_id.id), '|', ('ttype', '=', 'date'),
                     ('ttype', '=', 'datetime')]).read(['id', 'name'])
                for field in datetime_field_list:
                    if field['name'] == 'create_date':
                        rec.tele_date_filter_field_2 = field['id']
            else:
                rec.tele_date_filter_field_2 = False
                rec.tele_domain_extension_2 = False

    # Writing separate function to fetch dashboard item data
    def tele_fetch_model_data_2(self, tele_model_name, tele_domain, tele_func, rec, domain=[]):
        data = 0
        try:
            if tele_domain and tele_domain != '[]' and tele_model_name:
                proper_domain = self.tele_convert_into_proper_domain_2(tele_domain, rec, domain)
                if tele_func == 'search_count':
                    data = self.env[tele_model_name].search_count(proper_domain)
                elif tele_func == 'read_group':
                    data = self.env[tele_model_name].read_group(proper_domain, [rec.tele_record_field_2.name], [],
                                                              lazy=False)
            elif tele_model_name:
                # Have to put extra if condition here because on load,model giving False value
                proper_domain = self.tele_convert_into_proper_domain_2(False, rec, domain)
                if tele_func == 'search_count':
                    data = self.env[tele_model_name].search_count(proper_domain)

                elif tele_func == 'read_group':
                    data = self.env[tele_model_name].read_group(proper_domain, [rec.tele_record_field_2.name], [],
                                                              lazy=False)
            else:
                return []
        except Exception as e:
            return []
        return data

    @api.onchange('tele_date_filter_selection_2')
    def tele_set_date_filter_2(self):
        for rec in self:
            if (not rec.tele_date_filter_selection_2) or rec.tele_date_filter_selection_2 == "l_none":
                rec.tele_item_start_date_2 = rec.tele_item_end_date = False
            elif rec.tele_date_filter_selection_2 != 'l_custom':
                tele_date_data = tele_get_date(rec.tele_date_filter_selection_2, self, rec.tele_date_filter_field_2.ttype)
                rec.tele_item_start_date_2 = tele_date_data["selected_start_date"]
                rec.tele_item_end_date_2 = tele_date_data["selected_end_date"]

    def tele_convert_into_proper_domain_2(self, tele_domain_2, rec, domain=[]):
        if tele_domain_2 and "%UID" in tele_domain_2:
            tele_domain_2 = tele_domain_2.replace('"%UID"', str(self.env.user.id))
        if tele_domain_2 and "%MYCOMPANY" in tele_domain_2:
            tele_domain_2 = tele_domain_2.replace('"%MYCOMPANY"', str(self.env.company.id))

        tele_date_domain = False

        if rec.tele_date_filter_field_2:
            if not rec.tele_date_filter_selection_2 or rec.tele_date_filter_selection_2 == "l_none":
                selected_start_date = self._context.get('teleDateFilterStartDate', False)
                selected_end_date = self._context.get('teleDateFilterEndDate', False)
                tele_is_def_custom_filter = self._context.get('teleIsDefultCustomDateFilter', False)
                tele_timezone = self._context.get('tz') or self.env.user.tz
                if selected_start_date and selected_end_date and rec.tele_date_filter_field_2.ttype == 'datetime' and not tele_is_def_custom_filter:
                    selected_start_date = tele_convert_into_utc(selected_start_date, tele_timezone)
                    selected_end_date = tele_convert_into_utc(selected_end_date, tele_timezone)
                if selected_start_date and selected_end_date and rec.tele_date_filter_field_2.ttype == 'date' and tele_is_def_custom_filter:
                    selected_start_date = tele_convert_into_local(selected_start_date, tele_timezone)
                    selected_end_date = tele_convert_into_local(selected_end_date, tele_timezone)
                if self._context.get('teleDateFilterSelection', False) and self._context['teleDateFilterSelection'] not in [
                    'l_none', 'l_custom']:
                    tele_date_data = tele_get_date(self._context.get('teleDateFilterSelection'), self,
                                               rec.tele_date_filter_field_2.ttype)
                    selected_start_date = tele_date_data["selected_start_date"]
                    selected_end_date = tele_date_data["selected_end_date"]

                if selected_end_date and not selected_start_date:
                    tele_date_domain = [
                        (rec.tele_date_filter_field_2.name, "<=",
                         selected_end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
                elif selected_start_date and not selected_end_date:
                    tele_date_domain = [
                        (rec.tele_date_filter_field_2.name, ">=",
                         selected_start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
                else:
                    if selected_end_date and selected_start_date:
                        tele_date_domain = [
                            (rec.tele_date_filter_field_2.name, ">=",
                             selected_start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                            (rec.tele_date_filter_field_2.name, "<=",
                             selected_end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
            else:
                if rec.tele_date_filter_selection_2 and rec.tele_date_filter_selection_2 != 'l_custom':
                    tele_date_data = tele_get_date(rec.tele_date_filter_selection_2, self, rec.tele_date_filter_field_2.ttype)
                    selected_start_date = tele_date_data["selected_start_date"]
                    selected_end_date = tele_date_data["selected_end_date"]
                else:
                    selected_start_date = False
                    selected_end_date = False
                    if rec.tele_item_start_date_2 or rec.tele_item_end_date_2:
                        selected_start_date = rec.tele_item_start_date_2
                        selected_end_date = rec.tele_item_end_date_2
                        if rec.tele_date_filter_field_2.ttype == 'date' and rec.tele_item_start_date_2 and rec.tele_item_end_date_2:
                            tele_timezone = self._context.get('tz') or self.env.user.tz
                            selected_start_date = tele_convert_into_local(rec.tele_item_start_date_2, tele_timezone)
                            selected_end_date = tele_convert_into_local(rec.tele_item_end_date_2, tele_timezone)

                if selected_start_date and selected_end_date:
                    if rec.tele_compare_period_2:
                        tele_compare_period_2 = abs(rec.tele_compare_period_2)
                        if tele_compare_period_2 > 100:
                            tele_compare_period_2 = 100
                        if rec.tele_compare_period_2 > 0:
                            selected_end_date = selected_end_date + (
                                    selected_end_date - selected_start_date) * tele_compare_period_2
                            if rec.tele_date_filter_field.ttype == "date" and rec.tele_date_filter_selection == 'l_day':
                                selected_end_date = selected_end_date + timedelta(days=tele_compare_period_2)
                        elif rec.tele_compare_period_2 < 0:
                            selected_start_date = selected_start_date - (
                                    selected_end_date - selected_start_date) * tele_compare_period_2
                            if rec.tele_date_filter_field.ttype == "date" and rec.tele_date_filter_selection == 'l_day':
                                selected_start_date = selected_end_date - timedelta(days=tele_compare_period_2)

                    if rec.tele_year_period_2 and rec.tele_year_period_2 != 0:
                        abs_year_period_2 = abs(rec.tele_year_period_2)
                        sign_yp = rec.tele_year_period_2 / abs_year_period_2
                        if abs_year_period_2 > 100:
                            abs_year_period_2 = 100
                        date_field_name = rec.tele_date_filter_field_2.name

                        tele_date_domain = ['&', (date_field_name, ">=",
                                                fields.datetime.strftime(selected_start_date,
                                                                         DEFAULT_SERVER_DATETIME_FORMAT)),
                                          (date_field_name, "<=",
                                           fields.datetime.strftime(selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT))]

                        for p in range(1, abs_year_period_2 + 1):
                            tele_date_domain.insert(0, '|')
                            tele_date_domain.extend(['&', (date_field_name, ">=", fields.datetime.strftime(
                                selected_start_date - relativedelta.relativedelta(years=p) * sign_yp,
                                DEFAULT_SERVER_DATETIME_FORMAT)),
                                                   (date_field_name, "<=", fields.datetime.strftime(
                                                       selected_end_date - relativedelta.relativedelta(
                                                           years=p) * sign_yp,
                                                       DEFAULT_SERVER_DATETIME_FORMAT))])
                    else:
                        if rec.tele_date_filter_field_2:
                            selected_start_date = fields.datetime.strftime(selected_start_date,
                                                                           DEFAULT_SERVER_DATETIME_FORMAT)
                            selected_end_date = fields.datetime.strftime(selected_end_date,
                                                                         DEFAULT_SERVER_DATETIME_FORMAT)
                            tele_date_domain = [(rec.tele_date_filter_field_2.name, ">=", selected_start_date),
                                              (rec.tele_date_filter_field_2.name, "<=", selected_end_date)]
                        else:
                            tele_date_domain = []
                elif selected_start_date and rec.tele_date_filter_field_2:
                    selected_start_date = fields.datetime.strftime(selected_start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    tele_date_domain = [(rec.tele_date_filter_field_2.name, ">=", selected_start_date)]
                elif selected_end_date and rec.tele_date_filter_field_2:
                    selected_end_date = fields.datetime.strftime(selected_end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                    tele_date_domain = [(rec.tele_date_filter_field_2.name, "<=", selected_end_date)]
        else:
            tele_date_domain = []

        proper_domain = safe_eval(tele_domain_2) if tele_domain_2 else []
        if tele_date_domain:
            proper_domain.extend(tele_date_domain)
        if rec.tele_domain_extension_2:
            tele_domain_extension = rec.tele_convert_domain_extension(rec.tele_domain_extension_2, rec)
            proper_domain.extend(tele_domain_extension)
        if domain:
            proper_domain.extend(domain)

        return proper_domain

    def tele_fetch_chart_data(self, tele_model_name, tele_chart_domain, tele_chart_measure_field_with_type,
                            tele_chart_measure_field_with_type_2,
                            tele_chart_measure_field, tele_chart_measure_field_2,
                            tele_chart_groupby_relation_field, tele_chart_date_groupby, tele_chart_groupby_type, orderby,
                            limit, chart_count, tele_chart_measure_field_ids, tele_chart_measure_field_2_ids,
                            tele_chart_groupby_relation_field_id, tele_chart_data):

        if tele_chart_groupby_type == "date_type":
            tele_chart_groupby_field = tele_chart_groupby_relation_field + ":" + tele_chart_date_groupby
        else:
            tele_chart_groupby_field = tele_chart_groupby_relation_field

        try:
            if self.tele_fill_temporal and tele_chart_date_groupby not in ['minute', 'hour']:
                tele_chart_records = self.env[tele_model_name].with_context(fill_temporal=True) \
                    .read_group(tele_chart_domain,
                                list(set(tele_chart_measure_field_with_type + tele_chart_measure_field_with_type_2 +
                                         [tele_chart_groupby_relation_field])), [tele_chart_groupby_field],
                                orderby=orderby, limit=limit, lazy=False)
            else:
                tele_chart_records = self.env[tele_model_name] \
                    .read_group(tele_chart_domain,
                                list(set(tele_chart_measure_field_with_type + tele_chart_measure_field_with_type_2 +
                                         [tele_chart_groupby_relation_field])), [tele_chart_groupby_field],
                                orderby=orderby, limit=limit, lazy=False)
        except Exception as e:
            tele_chart_records = []
            pass
        tele_chart_data['groupby'] = tele_chart_groupby_field
        if tele_chart_groupby_type == "relational_type":
            tele_chart_data['groupByIds'] = []

        for res in tele_chart_records:
            is_tele_index = False
            tele_index = False
            if all(measure_field in res for measure_field in tele_chart_measure_field):
                if tele_chart_groupby_type == "relational_type":
                    if res[tele_chart_groupby_field]:
                        tele_chart_data['groupByIds'].append(res[tele_chart_groupby_field][0])
                        label = res[tele_chart_groupby_field][1]._value
                    else:
                        label = res[tele_chart_groupby_field]
                elif tele_chart_groupby_type == "selection":
                    selection = res[tele_chart_groupby_field]
                    if selection:
                        label = dict(self.env[tele_model_name].fields_get(allfields=[tele_chart_groupby_field])
                                     [tele_chart_groupby_field]['selection'])[selection]
                    else:
                        label = selection
                else:
                    label = res[tele_chart_groupby_field]

                tele_chart_data['domains'].append(res.get('__domain', []))
                if label in tele_chart_data['labels']:
                    tele_index = tele_chart_data['labels'].index(label)
                    is_tele_index = True

                else:
                    tele_chart_data['labels'].append(label)

                counter = 0
                if tele_chart_measure_field:
                    if tele_chart_measure_field_2:
                        index = 0
                        for field_rec in tele_chart_measure_field_2:
                            tele_groupby_equal_measures = res.get(tele_chart_groupby_relation_field + "_count",
                                                                False) or res.get("__count", False) \
                                if res.get(tele_chart_groupby_relation_field + "_count", False) or res.get("__count",
                                                                                                         False) \
                                   and tele_chart_measure_field_2_ids[index] == tele_chart_groupby_relation_field_id \
                                else 1
                            try:
                                if res.get('__count', False):
                                    data = res[field_rec] * tele_groupby_equal_measures \
                                        if chart_count == 'sum' else \
                                        res[field_rec]
                                else:
                                    data = 0
                                if is_tele_index:
                                    if chart_count == 'sum':
                                        tele_chart_data['datasets'][counter]['data'][tele_index] += data
                                    else:
                                        tele_chart_data['datasets'][counter]['data'][tele_index] = \
                                            (tele_chart_data['datasets'][counter]['data'][tele_index] + data) / 2
                                    counter += 1
                                    index += 1
                                    continue
                            except ZeroDivisionError:
                                data = 0
                            tele_chart_data['datasets'][counter]['data'].append(data)
                            counter += 1
                            index += 1

                    index = 0
                    for field_rec in tele_chart_measure_field:
                        tele_groupby_equal_measures = res.get(tele_chart_groupby_relation_field + "_count",
                                                            False) or res.get("__count", False) \
                            if res.get(tele_chart_groupby_relation_field + "_count", False) or res.get("__count", False) \
                               and tele_chart_measure_field_ids[index] == tele_chart_groupby_relation_field_id \
                            else 1
                        try:
                            if res.get('__count', False):
                                data = res[field_rec] * tele_groupby_equal_measures \
                                    if chart_count == 'sum' else \
                                    res[field_rec]
                            else:
                                data = 0
                            if is_tele_index:
                                if chart_count == 'sum':
                                    tele_chart_data['datasets'][counter]['data'][tele_index] += data
                                else:
                                    tele_chart_data['datasets'][counter]['data'][tele_index] = \
                                        (tele_chart_data['datasets'][counter]['data'][tele_index] + data) / 2
                                counter += 1
                                index += 1
                                continue
                        except ZeroDivisionError:
                            data = 0
                        tele_chart_data['datasets'][counter]['data'].append(data)
                        counter += 1
                        index += 1

                else:
                    if res.get('__count'):
                        count = res[tele_chart_groupby_relation_field + "_count"] \
                            if res.get((tele_chart_groupby_relation_field + "_count"), False) else res['__count']
                    else:
                        count = 0
                    data = count
                    tele_chart_data['datasets'][0]['data'].append(data)

        return tele_chart_data

    @api.model
    def tele_fetch_drill_down_data(self, item_id, domain, sequence):

        record = self.browse(int(item_id))
        tele_chart_data = {'labels': [], 'datasets': [], 'tele_show_second_y_scale': False, 'domains': [],
                         'previous_domain': domain, 'tele_currency': 0, 'tele_field': "", 'tele_selection': "", }
        if record.tele_unit and record.tele_unit_selection == 'monetary':
            tele_chart_data['tele_selection'] += record.tele_unit_selection
            tele_chart_data['tele_currency'] += record.env.user.company_id.currency_id.id
        elif record.tele_unit and record.tele_unit_selection == 'custom':
            tele_chart_data['tele_selection'] += record.tele_unit_selection
            if record.tele_chart_unit:
                tele_chart_data['tele_field'] += record.tele_chart_unit

        # If count chart data type:
        action_lines = record.tele_action_lines.sorted(key=lambda r: r.sequence)
        action_line = action_lines[sequence]
        tele_chart_type = action_line.tele_chart_type if action_line.tele_chart_type else record.tele_dashboard_item_type
        tele_list_view_data = {'label': [], 'type': 'grouped',
                             'data_rows': [], 'model': record.tele_model_name, 'previous_domain': domain, }
        if action_line.tele_chart_type == 'tele_list_view':
            if record.tele_dashboard_item_type == 'tele_list_view':
                tele_chart_list_measure = record.tele_list_view_group_fields
            else:
                tele_chart_list_measure = record.tele_chart_measure_field

            tele_list_fields = []
            # if action_line.tele_sort_by_field:
            #     tele_list_fields.append(action_line.tele_sort_by_field.name)
            orderby = action_line.tele_sort_by_field.name if action_line.tele_sort_by_field else "id"
            if action_line.tele_sort_by_order:
                orderby = orderby + " " + action_line.tele_sort_by_order
            limit = action_line.tele_record_limit \
                if action_line.tele_record_limit and action_line.tele_record_limit > 0 else False
            tele_count = 0
            for tele in record.tele_action_lines:
                tele_count += 1
            if action_line.tele_item_action_field.ttype == 'many2one':
                tele_list_view_data['list_view_type'] = 'relational_type'
                tele_list_view_data['groupby'] = action_line.tele_item_action_field.name
                tele_list_fields.append(action_line.tele_item_action_field.name)
                tele_list_view_data['label'].append(action_line.tele_item_action_field.field_description)
                for res in tele_chart_list_measure:
                    tele_list_fields.append(res.name)
                    tele_list_view_data['label'].append(res.field_description)

                tele_list_view_records = self.env[record.tele_model_name] \
                    .read_group(domain, tele_list_fields, [action_line.tele_item_action_field.name], orderby=orderby,
                                limit=limit, lazy=False)
                for res in tele_list_view_records:

                    counter = 0
                    data_row = {'id': res[action_line.tele_item_action_field.name][0] if res[
                        action_line.tele_item_action_field.name] else res[action_line.tele_item_action_field.name],
                                'data': [],
                                'domain': json.dumps(res['__domain']), 'sequence': sequence + 1,
                                'last_seq': tele_count, 'tele_column_type': []}
                    for field_rec in tele_list_fields:
                        if counter == 0:
                            data_row['data'].append(res[field_rec][1]._value if res[field_rec] else "False")
                        else:
                            data_row['data'].append(res[field_rec])
                        counter += 1
                        data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                    tele_list_view_data['data_rows'].append(data_row)

            elif action_line.tele_item_action_field.ttype == 'date' or \
                    action_line.tele_item_action_field.ttype == 'datetime':
                tele_list_view_data['list_view_type'] = 'date_type'
                tele_list_field = []
                tele_list_view_data[
                    'groupby'] = action_line.tele_item_action_field.name + ':' + action_line.tele_item_action_date_groupby
                tele_list_field.append(
                    action_line.tele_item_action_field.name + ':' + action_line.tele_item_action_date_groupby)
                tele_list_fields.append(action_line.tele_item_action_field.name)
                tele_list_view_data['label'].append(
                    action_line.tele_item_action_field.field_description)
                for res in tele_chart_list_measure:
                    tele_list_fields.append(res.name)
                    tele_list_field.append(res.name)
                    tele_list_view_data['label'].append(res.field_description)

                tele_list_view_records = self.env[record.tele_model_name] \
                    .read_group(domain, tele_list_fields, [action_line.tele_item_action_field.name + ':' +
                                                         action_line.tele_item_action_date_groupby], orderby=orderby,
                                limit=limit, lazy=False)

                for res in tele_list_view_records:
                    counter = 0
                    data_row = {'data': [],
                                'domain': json.dumps(res['__domain']), 'sequence': sequence + 1,
                                'last_seq': tele_count, 'tele_column_type': []}
                    for field_rec in tele_list_field:
                        data_row['data'].append(res[field_rec])
                        data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                    tele_list_view_data['data_rows'].append(data_row)

            elif action_line.tele_item_action_field.ttype == 'selection':
                tele_list_view_data['list_view_type'] = 'selection'
                tele_list_view_data['groupby'] = action_line.tele_item_action_field.name
                tele_selection_field = action_line.tele_item_action_field.name
                tele_list_view_data['label'].append(action_line.tele_item_action_field.field_description)
                for res in tele_chart_list_measure:
                    tele_list_fields.append(res.name)
                    tele_list_view_data['label'].append(res.field_description)

                tele_list_view_records = self.env[record.tele_model_name] \
                    .read_group(domain, tele_list_fields, [action_line.tele_item_action_field.name], orderby=orderby,
                                limit=limit, lazy=False)
                for res in tele_list_view_records:
                    counter = 0
                    data_row = {'data': [],
                                'domain': json.dumps(res['__domain']), 'sequence': sequence + 1,
                                'last_seq': tele_count, 'tele_column_type': []}
                    if res[tele_selection_field]:
                        data_row['data'].append(dict(
                            self.env[record.tele_model_name].fields_get(allfields=tele_selection_field)
                            [tele_selection_field]['selection'])[res[tele_selection_field]])
                    else:
                        data_row['data'].append(" ")
                    data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                    for field_rec in tele_list_fields:
                        data_row['data'].append(res[field_rec])
                        data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                    tele_list_view_data['data_rows'].append(data_row)

            else:
                tele_list_view_data['list_view_type'] = 'other'
                tele_list_view_data['groupby'] = action_line.tele_item_action_field.name
                tele_list_fields.append(action_line.tele_item_action_field.name)
                tele_list_view_data['label'].append(action_line.tele_item_action_field.field_description)
                for res in tele_chart_list_measure:
                    if action_line.tele_item_action_field.name != res.name:
                        tele_list_view_data['label'].append(res.field_description)
                        tele_list_fields.append(res.name)

                tele_list_view_records = self.env[record.tele_model_name] \
                    .read_group(domain, tele_list_fields, [action_line.tele_item_action_field.name], orderby=orderby,
                                limit=limit, lazy=False)
                for res in tele_list_view_records:
                    if all(list_fields in res for list_fields in tele_list_fields):
                        counter = 0
                        data_row = {'id': action_line.tele_item_action_field.name, 'data': [],
                                    'domain': json.dumps(res['__domain']), 'sequence': sequence + 1,
                                    'last_seq': tele_count, 'tele_column_type': []}

                        for field_rec in tele_list_fields:
                            if counter == 0:
                                data_row['data'].append(res[field_rec])
                            else:
                                if action_line.tele_item_action_field.name == field_rec:
                                    data_row['data'].append(res[field_rec] * (
                                        res.get(field_rec + '_count', False) if res.get(field_rec + '_count',
                                                                                        False) else res.get('__count')))
                                else:
                                    data_row['data'].append(res[field_rec])
                            counter += 1
                            data_row['tele_column_type'].append(self.tele_chart_relation_groupby.ttype)
                        tele_list_view_data['data_rows'].append(data_row)
            if record.tele_multiplier_active:
                for tele_multiplier in record.tele_multiplier_lines:
                    label = tele_multiplier.tele_multiplier_fields.field_description
                    if label in tele_list_view_data['label']:
                        index = tele_list_view_data['label'].index(label)
                        for i in range(0, len(tele_list_view_data['data_rows'])):
                            data_values = tele_list_view_data['data_rows'][i]['data'][
                                              index] * tele_multiplier.tele_multiplier_value
                            tele_list_view_data['data_rows'][i]['data'][index] = data_values
            return {"tele_list_view_data": json.dumps(tele_list_view_data), "tele_list_view_type": "grouped",
                    'sequence': sequence + 1, }
        else:
            tele_chart_measure_field = []
            tele_chart_measure_field_with_type = []
            tele_chart_measure_field_ids = []
            tele_chart_measure_field_2 = []
            tele_chart_measure_field_with_type_2 = []
            tele_chart_measure_field_2_ids = []
            if record.tele_chart_data_count_type == "count":
                if not action_line.tele_sort_by_field:
                    tele_chart_measure_field_with_type.append('count:count(id)')
                elif action_line.tele_sort_by_field:
                    if not action_line.tele_sort_by_field.ttype == "datetime":
                        tele_chart_measure_field_with_type.append(action_line.tele_sort_by_field.name + ':' + 'sum')
                    else:
                        tele_chart_measure_field_with_type.append(action_line.tele_sort_by_field.name)

                tele_chart_data['datasets'].append({'data': [], 'label': "Count"})
            else:
                if tele_chart_type == 'tele_bar_chart':
                    if record.tele_chart_measure_field_2:
                        tele_chart_data['tele_show_second_y_scale'] = True

                    for res in record.tele_chart_measure_field_2:
                        if record.tele_chart_data_count_type == 'sum':
                            tele_data_count_type = 'sum'
                        elif record.tele_chart_data_count_type == 'average':
                            tele_data_count_type = 'avg'
                        else:
                            raise ValidationError(_('Please chose any Data Type!'))
                        tele_chart_measure_field_2.append(res.name)
                        tele_chart_measure_field_with_type_2.append(res.name + ':' + tele_data_count_type)
                        tele_chart_measure_field_2_ids.append(res.id)
                        tele_chart_data['datasets'].append(
                            {'data': [], 'label': res.field_description, 'type': 'line', 'yAxisID': 'y-axis-1'})
                if record.tele_dashboard_item_type == 'tele_list_view':
                    for res in record.tele_list_view_group_fields:
                        tele_chart_measure_field.append(res.name)
                        tele_chart_measure_field_with_type.append(res.name + ':' + 'sum')
                        tele_chart_measure_field_ids.append(res.id)
                        tele_chart_data['datasets'].append({'data': [], 'label': res.field_description})
                else:
                    for res in record.tele_chart_measure_field:
                        if record.tele_chart_data_count_type == 'sum':
                            tele_data_count_type = 'sum'
                        elif record.tele_chart_data_count_type == 'average':
                            tele_data_count_type = 'avg'
                        else:
                            raise ValidationError(_('Please chose any Data Type!'))
                        tele_chart_measure_field.append(res.name)
                        tele_chart_measure_field_with_type.append(res.name + ':' + tele_data_count_type)
                        tele_chart_measure_field_ids.append(res.id)
                        tele_chart_data['datasets'].append({'data': [], 'label': res.field_description})

            tele_chart_groupby_relation_field = action_line.tele_item_action_field.name
            tele_chart_relation_type = action_line.tele_item_action_field_type
            tele_chart_date_group_by = action_line.tele_item_action_date_groupby
            tele_chart_groupby_relation_field_id = action_line.tele_item_action_field.id
            # orderby = action_line.tele_sort_by_field.name if action_line.tele_sort_by_field else "id"
            if record.tele_chart_data_count_type == "count" and not self.tele_fill_temporal and not action_line.tele_sort_by_field:
                orderby = 'count'
            else:
                orderby = action_line.tele_sort_by_field.name if action_line.tele_sort_by_field else "id"
            if action_line.tele_sort_by_order:
                orderby = orderby + " " + action_line.tele_sort_by_order
            limit = action_line.tele_record_limit if action_line.tele_record_limit and action_line.tele_record_limit > 0 else False

            if tele_chart_type != "tele_bar_chart":
                tele_chart_measure_field_2 = []
                tele_chart_measure_field_2_ids = []

            tele_chart_data = record.tele_fetch_chart_data(record.tele_model_name, domain,
                                                       tele_chart_measure_field_with_type,
                                                       tele_chart_measure_field_with_type_2,
                                                       tele_chart_measure_field,
                                                       tele_chart_measure_field_2,
                                                       tele_chart_groupby_relation_field, tele_chart_date_group_by,
                                                       tele_chart_relation_type,
                                                       orderby, limit, record.tele_chart_data_count_type,
                                                       tele_chart_measure_field_ids,
                                                       tele_chart_measure_field_2_ids, tele_chart_groupby_relation_field_id,
                                                       tele_chart_data)
            if record.tele_multiplier_active:
                for tele_multiplier in record.tele_multiplier_lines:
                    for i in range(0,len(tele_chart_data['datasets'])):
                        if tele_multiplier.tele_multiplier_fields.field_description in tele_chart_data['datasets'][i]['label']:
                            data_values = tele_chart_data['datasets'][i]['data']
                            data_values = list(map(lambda x : tele_multiplier.tele_multiplier_value*x, data_values))
                            tele_chart_data['datasets'][i]['data'] = data_values
            return {
                'tele_chart_data': json.dumps(tele_chart_data),
                'tele_chart_type': tele_chart_type,
                'sequence': sequence + 1,
            }

    @api.model
    def tele_get_start_end_date(self, model_name, tele_chart_groupby_relation_field, ttype, tele_chart_domain,
                              tele_goal_domain):
        tele_start_end_date = {}
        try:
            model_field_start_date = \
                self.env[model_name].search(tele_chart_domain + [(tele_chart_groupby_relation_field, '!=', False)], limit=1,
                                            order=tele_chart_groupby_relation_field + " ASC")[
                    tele_chart_groupby_relation_field]
            model_field_end_date = \
                self.env[model_name].search(tele_chart_domain + [(tele_chart_groupby_relation_field, '!=', False)], limit=1,
                                            order=tele_chart_groupby_relation_field + " DESC")[
                    tele_chart_groupby_relation_field]
        except Exception as e:
            model_field_start_date = model_field_end_date = False
            pass
        # if model_field_start_date and model_field_end_date:
        #     goal_model_start_date = \
        #         self.env['tele_dashboard_ninja.item_goal'].search([('tele_goal_date', '>=', model_field_start_date.strftime("%Y-%m-%d")),
        #                            ('tele_goal_date', '<=', model_field_end_date.strftime("%Y-%m-%d"))], limit=1,
        #                                                         order='tele_goal_date ASC')['tele_goal_date']
        #     goal_model_end_date = \
        #         self.env['tele_dashboard_ninja.item_goal'].search([('tele_goal_date', '>=', model_field_start_date.strftime("%Y-%m-%d")),
        #                            ('tele_goal_date', '<=', model_field_end_date.strftime("%Y-%m-%d"))], limit=1,
        #                                                         order='tele_goal_date DESC')['tele_goal_date']
        # else:

        goal_model_start_date = \
            self.env['tele_dashboard_ninja.item_goal'].search(tele_goal_domain, limit=1,
                                                            order='tele_goal_date ASC')['tele_goal_date']
        goal_model_end_date = \
            self.env['tele_dashboard_ninja.item_goal'].search(tele_goal_domain, limit=1,
                                                            order='tele_goal_date DESC')['tele_goal_date']

        if model_field_start_date and ttype == "date":
            model_field_end_date = datetime.combine(model_field_end_date, datetime.min.time())
            model_field_start_date = datetime.combine(model_field_start_date, datetime.min.time())

        if model_field_start_date and goal_model_start_date:
            goal_model_start_date = datetime.combine(goal_model_start_date, datetime.min.time())
            goal_model_end_date = datetime.combine(goal_model_end_date, datetime.max.time())
            if model_field_start_date < goal_model_start_date:
                tele_start_end_date['start_date'] = model_field_start_date.strftime("%Y-%m-%d 00:00:00")
            else:
                tele_start_end_date['start_date'] = goal_model_start_date.strftime("%Y-%m-%d 00:00:00")
            if model_field_end_date > goal_model_end_date:
                tele_start_end_date['end_date'] = model_field_end_date.strftime("%Y-%m-%d 23:59:59")
            else:
                tele_start_end_date['end_date'] = goal_model_end_date.strftime("%Y-%m-%d 23:59:59")

        elif model_field_start_date and not goal_model_start_date:
            tele_start_end_date['start_date'] = model_field_start_date.strftime("%Y-%m-%d 00:00:00")
            tele_start_end_date['end_date'] = model_field_end_date.strftime("%Y-%m-%d 23:59:59")

        elif goal_model_start_date and not model_field_start_date:
            tele_start_end_date['start_date'] = goal_model_start_date.strftime("%Y-%m-%d 00:00:00")
            tele_start_end_date['end_date'] = goal_model_end_date.strftime("%Y-%m-%d 23:59:59")
        else:
            tele_start_end_date['start_date'] = False
            tele_start_end_date['end_date'] = False

        return tele_start_end_date

    # List View pagination
    @api.model
    def tele_get_next_offset(self, tele_item_id, offset, item_domain=[]):
        record = self.browse(tele_item_id)
        tele_offset = offset['offset']
        tele_list_domain = self.tele_convert_into_proper_domain(record.tele_domain, self, item_domain)
        if self.tele_list_view_type == 'grouped':
            orderby = record.tele_sort_by_field.id
            sort_order = record.tele_sort_by_order
            tele_list_view_data = self.get_list_view_record(orderby, sort_order, tele_list_domain, teleoffset=int(tele_offset))

        else:
            tele_list_view_data = self.tele_fetch_list_view_data(record, tele_list_domain, offset=int(tele_offset))

        return {
            'tele_list_view_data': json.dumps(tele_list_view_data),
            'offset': int(tele_offset) + 1,
            'next_offset': int(tele_offset) + len(tele_list_view_data['data_rows']),
            'limit': record.tele_record_data_limit if record.tele_record_data_limit else 0,
        }

    @api.model
    def get_sorted_month(self, display_format, ftype='date'):
        query = """
                    with d as (SELECT date_trunc(%(aggr)s, generate_series) AS timestamp FROM generate_series
                    (%(timestamp_begin)s::TIMESTAMP , %(timestamp_end)s::TIMESTAMP , %(aggr1)s::interval ))
                     select timestamp from d group by timestamp order by timestamp
                        """
        self.env.cr.execute(query, {
            'timestamp_begin': "2020-01-01 00:00:00",
            'timestamp_end': "2020-12-31 00:00:00",
            'aggr': 'month',
            'aggr1': '1 month'
        })

        dates = self.env.cr.fetchall()
        locale = self._context.get('lang') or 'en_US'
        tz_convert = self._context.get('tz')
        return [self.format_label(d[0], ftype, display_format, tz_convert, locale) for d in dates]

    # Fix Order BY : maybe revert old code
    @api.model
    def generate_timeserise(self, date_begin, date_end, aggr, ftype='date'):
        query = """
                    with d as (SELECT date_trunc(%(aggr)s, generate_series) AS timestamp FROM generate_series
                    (%(timestamp_begin)s::TIMESTAMP , %(timestamp_end)s::TIMESTAMP , '1 hour'::interval )) 
                    select timestamp from d group by timestamp order by timestamp
                """

        self.env.cr.execute(query, {
            'timestamp_begin': date_begin,
            'timestamp_end': date_end,
            'aggr': aggr,
            'aggr1': '1 ' + aggr
        })
        dates = self.env.cr.fetchall()
        display_formats = {
            # Careful with week/year formats:
            #  - yyyy (lower) must always be used, except for week+year formats
            #  - YYYY (upper) must always be used for week+year format
            #         e.g. 2006-01-01 is W52 2005 in some locales (de_DE),
            #                         and W1 2006 for others
            #
            # Mixing both formats, e.g. 'MMM YYYY' would yield wrong results,
            # such as 2006-01-01 being formatted as "January 2005" in some locales.
            # Cfr: http://babel.pocoo.org/en/latest/dates.html#date-fields
            'minute': 'hh:mm dd MMM',
            'hour': 'hh:00 dd MMM',
            'day': 'dd MMM yyyy',  # yyyy = normal year
            'week': "'W'w YYYY",  # w YYYY = ISO week-year
            'month': 'MMMM yyyy',
            'quarter': 'QQQ yyyy',
            'year': 'yyyy',
        }

        display_format = display_formats[aggr]
        locale = self._context.get('lang') or 'en_US'
        tz_convert = self._context.get('tz')
        return [self.format_label(d[0], ftype, display_format, tz_convert, locale) for d in dates]

    @api.model
    def format_label(self, value, ftype, display_format, tz_convert, locale):

        tzinfo = None
        if ftype == 'datetime':
            if tz_convert:
                value = pytz.timezone(self._context['tz']).localize(value)
                tzinfo = value.tzinfo
            return babel.dates.format_datetime(value, format=display_format, tzinfo=tzinfo, locale=locale)
        else:

            if tz_convert:
                value = pytz.timezone(self._context['tz']).localize(value)
                tzinfo = value.tzinfo
            return babel.dates.format_date(value, format=display_format, locale=locale)

    def tele_sort_sub_group_by_records(self, tele_data, field_type, tele_chart_date_groupby, tele_sort_by_order,
                                     tele_chart_date_sub_groupby):
        if tele_data:
            reverse = False
            if tele_sort_by_order == 'DESC':
                reverse = True

            for data in tele_data:
                if field_type == 'date_type':
                    if tele_chart_date_groupby in ['minute', 'hour']:
                        if tele_chart_date_sub_groupby in ["month", "week", "quarter", "year"]:
                            tele_sorted_months = self.get_sorted_month("MMM")
                            data['value'].sort(key=lambda x: int(
                                str(tele_sorted_months.index(x['x'].split(" ")[2]) + 1) + x['x'].split(" ")[1] +
                                x['x'].split(" ")[0].replace(":", "")), reverse=reverse)
                        else:
                            data['value'].sort(key=lambda x: int(x['x'].replace(":", "")), reverse=reverse)
                    elif tele_chart_date_groupby == 'day' and tele_chart_date_sub_groupby in ["quarter", "year"]:
                        tele_sorted_days = self.generate_timeserise("2020-01-01 00:00:00", "2020-12-31 00:00:00",
                                                                  'day', "date")
                        b = [" ".join(x.split(" ")[0:2]) for x in tele_sorted_days]
                        data['value'].sort(key=lambda x: b.index(x['x']), reverse=reverse)
                    elif tele_chart_date_groupby == 'day' and tele_chart_date_sub_groupby not in ["quarter", "year"]:
                        data['value'].sort(key=lambda i: int(i['x']), reverse=reverse)
                    elif tele_chart_date_groupby == 'week':
                        data['value'].sort(key=lambda i: int(i['x'][1:]), reverse=reverse)
                    elif tele_chart_date_groupby == 'month':
                        tele_sorted_months = self.generate_timeserise("2020-01-01 00:00:00", "2020-12-31 00:00:00",
                                                                    'month', "date")
                        b = [" ".join(x.split(" ")[0:1]) for x in tele_sorted_months]
                        data['value'].sort(key=lambda x: b.index(x['x']), reverse=reverse)
                    elif tele_chart_date_groupby == 'quarter':
                        tele_sorted_months = self.generate_timeserise("2020-01-01 00:00:00", "2020-12-31 00:00:00",
                                                                    'quarter', "date")
                        b = [" ".join(x.split(" ")[:-1]) for x in tele_sorted_months]
                        data['value'].sort(key=lambda x: b.index(x['x']), reverse=reverse)
                    elif tele_chart_date_groupby == 'year':
                        data['value'].sort(key=lambda i: int(i['x']), reverse=reverse)
                else:
                    data['value'].sort(key=lambda i: i['x'], reverse=reverse)

        return tele_data

    @api.onchange('tele_domain_2')
    def tele_onchange_check_domain_2_onchange(self):
        if self.tele_domain_2:
            proper_domain_2 = []
            try:
                tele_domain_2 = self.tele_domain_2
                if "%UID" in tele_domain_2:
                    tele_domain_2 = tele_domain_2.replace("%UID", str(self.env.user.id))
                if "%MYCOMPANY" in tele_domain_2:
                    tele_domain_2 = tele_domain_2.replace("%MYCOMPANY", str(self.env.company.id))
                tele_domain_2 = safe_eval(tele_domain_2)

                for element in tele_domain_2:
                    proper_domain_2.append(element) if type(element) != list else proper_domain_2.append(tuple(element))
                self.env[self.tele_model_name_2].search_count(proper_domain_2)
            except Exception:
                raise UserError("Invalid Domain")

    @api.onchange('tele_domain')
    def tele_onchange_check_domain_onchange(self):
        if self.tele_domain:
            proper_domain = []
            try:
                tele_domain = self.tele_domain
                if "%UID" in tele_domain:
                    tele_domain = tele_domain.replace("%UID", str(self.env.user.id))
                if "%MYCOMPANY" in tele_domain:
                    tele_domain = tele_domain.replace("%MYCOMPANY", str(self.env.company.id))
                tele_domain = safe_eval(tele_domain)
                for element in tele_domain:
                    proper_domain.append(element) if type(element) != list else proper_domain.append(tuple(element))
                self.env[self.tele_model_name].search_count(proper_domain)
            except Exception:
                raise UserError("Invalid Domain")


class TeleDashboardItemsGoal(models.Model):
    _name = 'tele_dashboard_ninja.item_goal'
    _description = 'Dashboard Ninja Items Goal Lines'

    tele_goal_date = fields.Date(string="Date")
    tele_goal_value = fields.Float(string="Value")

    tele_dashboard_item = fields.Many2one('tele_dashboard_ninja.item', string="Dashboard Item")


class TeleDashboardItemsActions(models.Model):
    _name = 'tele_dashboard_ninja.item_action'
    _description = 'Dashboard Ninja Items Action Lines'

    tele_item_action_field = fields.Many2one('ir.model.fields',
                                           domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),('store','=',True),"
                                                  "('ttype','!=','binary'),('ttype','!=','many2many'), "
                                                  "('ttype','!=','one2many')]",
                                           string="Action Group By")

    tele_item_action_field_type = fields.Char(compute="tele_get_item_action_type", compute_sudo=False)

    tele_item_action_date_groupby = fields.Selection([('minute', 'Minute'),
                                                    ('hour', 'Hour'),
                                                    ('day', 'Day'),
                                                    ('week', 'Week'),
                                                    ('month', 'Month'),
                                                    ('quarter', 'Quarter'),
                                                    ('year', 'Year'),
                                                    ], string="Group By Date")

    tele_chart_type = fields.Selection([('tele_bar_chart', 'Bar Chart'),
                                      ('tele_horizontalBar_chart', 'Horizontal Bar Chart'),
                                      ('tele_line_chart', 'Line Chart'),
                                      ('tele_area_chart', 'Area Chart'),
                                      ('tele_pie_chart', 'Pie Chart'),
                                      ('tele_doughnut_chart', 'Doughnut Chart'),
                                      ('tele_polarArea_chart', 'Polar Area Chart'),
                                      ('tele_list_view', 'List View')],
                                     string="Item Type")

    tele_dashboard_item_id = fields.Many2one('tele_dashboard_ninja.item', string="Dashboard Item")
    tele_model_id = fields.Many2one('ir.model', related='tele_dashboard_item_id.tele_model_id')
    sequence = fields.Integer(string="Sequence")
    # For sorting and record limit
    tele_record_limit = fields.Integer(string="Record Limit")
    tele_sort_by_field = fields.Many2one('ir.model.fields',
                                       domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),('store','=',True),"
                                              "('ttype','!=','one2many'),('ttype','!=','many2one'),"
                                              "('ttype','!=','binary')]",
                                       string="Sort By Field")
    tele_sort_by_order = fields.Selection([('ASC', 'Ascending'), ('DESC', 'Descending')],
                                        string="Sort Order")

    @api.depends('tele_item_action_field')
    def tele_get_item_action_type(self):
        for rec in self:
            if rec.tele_item_action_field.ttype == 'datetime' or rec.tele_item_action_field.ttype == 'date':
                rec.tele_item_action_field_type = 'date_type'
            elif rec.tele_item_action_field.ttype == 'many2one':
                rec.tele_item_action_field_type = 'relational_type'
            elif rec.tele_item_action_field.ttype == 'selection':
                rec.tele_item_action_field_type = 'selection'

            else:
                rec.tele_item_action_field_type = 'none'

    @api.onchange('tele_item_action_date_groupby')
    def tele_check_date_group_by(self):
        for rec in self:
            if rec.tele_item_action_field.ttype == 'date' and rec.tele_item_action_date_groupby in ['hour', 'minute']:
                raise ValidationError(_('Action field: {} cannot be aggregated by {}').format(
                    rec.tele_item_action_field.display_name, rec.tele_item_action_date_groupby))

    @api.onchange('tele_item_action_field')
    def tele_onchange_item_action(self):
        for rec in self:
            if not (rec.tele_item_action_field.ttype == 'datetime' or rec.tele_item_action_field.ttype == 'date'):
                rec.tele_item_action_date_groupby = False

class TeleDashboardItemMultiplier(models.Model):
    _name = 'tele_dashboard_item.multiplier'
    _description = 'Dashboard Ninja Items Multiplier Lines'

    tele_dashboard_item_id = fields.Many2one('tele_dashboard_ninja.item', string="Dashboard Item")
    tele_model_id = fields.Many2one('ir.model', related='tele_dashboard_item_id.tele_model_id')
    tele_multiplier_value = fields.Float(string="Multiplier", default=1)
    tele_multiplier_fields = fields.Many2one('ir.model.fields',
                                           domain="[('model_id','=',tele_model_id),('name','!=','id'),('name','!=','sequence'),"
                                                  "('store','=',True),'|','|',"
                                                  "('ttype','=','integer'),('ttype','=','float'),"
                                                  "('ttype','=','monetary')]",
                                           string="Multiplier Field")