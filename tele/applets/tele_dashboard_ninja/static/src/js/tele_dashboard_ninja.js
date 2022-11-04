tele.define('tele_dashboard_ninja.tele_dashboard', function(require) {
    "use strict";

    var core = require('web.core');
    const { patch } = require('web.utils');
    const { WebClient } = require("@web/webclient/webclient");
//    var export = require('tele_dashboard_ninja.import_button');
    var Dialog = require('web.Dialog');
    var viewRegistry = require('web.view_registry');
    var _t = core._t;
    var QWeb = core.qweb;
    var utils = require('web.utils');
    var config = require('web.config');
    var framework = require('web.framework');
    var time = require('web.time');
    var datepicker = require("web.datepicker");

    const session = require('web.session');
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var framework = require('web.framework');
    var field_utils = require('web.field_utils');
    var TeleGlobalFunction = require('tele_dashboard_ninja.TeleGlobalFunction');

    var TeleQuickEditView = require('tele_dashboard_ninja.quick_edit_view');


    var TeleDashboardNinja = AbstractAction.extend({
        // To show or hide top control panel flag.
        hasControlPanel: false,

        dependencies: ['bus_service'],

        /**
         * @override
         */

        jsLibs: [
            '/tele_dashboard_ninja/static/lib/js/Chart.bundle.min.js',
            '/tele_dashboard_ninja/static/lib/js/gridstack-h5.js',
            '/tele_dashboard_ninja/static/lib/js/chartjs-plugin-datalabels.js',
            '/tele_dashboard_ninja/static/lib/js/pdfmake.min.js',
            '/tele_dashboard_ninja/static/lib/js/vfs_fonts.js',
        ],
        cssLibs: ['/tele_dashboard_ninja/static/lib/css/Chart.css',
            '/tele_dashboard_ninja/static/lib/css/Chart.min.css'
        ],

        init: function(parent, state, params) {
//            css_grid = $('.o_rtl').length>0 ?
            this._super.apply(this, arguments);
            this.reload_menu_option = {
                reload: state.context.tele_reload_menu,
                menu_id: state.context.tele_menu_id
            };
            this.tele_mode = 'active';
            this.action_manager = parent;
            this.controllerID = params.controllerID;
            this.name = "tele_dashboard";
            this.teleIsDashboardManager = false;
            this.teleDashboardEditMode = false;
            this.teleNewDashboardName = false;
            this.file_type_magic_word = {
                '/': 'jpg',
                'R': 'gif',
                'i': 'png',
                'P': 'svg+xml',
            };
            this.teleAllowItemClick = true;

            //Dn Filters Iitialization
            var l10n = _t.database.parameters;
            this.form_template = 'tele_dashboard_ninja_template_view';
            this.date_format = time.strftime_to_moment_format(_t.database.parameters.date_format)
            this.date_format = this.date_format.replace(/\bYY\b/g, "YYYY");
            this.datetime_format = time.strftime_to_moment_format((_t.database.parameters.date_format + ' ' + l10n.time_format))
            //            this.is_dateFilter_rendered = false;
            this.tele_date_filter_data;

            // Adding date filter selection options in dictionary format : {'id':{'days':1,'text':"Text to show"}}
            this.tele_date_filter_selections = {
                'l_none': _t('Date Filter'),
                'l_day': _t('Today'),
                't_week': _t('This Week'),
                't_month': _t('This Month'),
                't_quarter': _t('This Quarter'),
                't_year': _t('This Year'),
                'n_day': _t('Next Day'),
                'n_week': _t('Next Week'),
                'n_month': _t('Next Month'),
                'n_quarter': _t('Next Quarter'),
                'n_year': _t('Next Year'),
                'ls_day': _t('Last Day'),
                'ls_week': _t('Last Week'),
                'ls_month': _t('Last Month'),
                'ls_quarter': _t('Last Quarter'),
                'ls_year': _t('Last Year'),
                'l_week': _t('Last 7 days'),
                'l_month': _t('Last 30 days'),
                'l_quarter': _t('Last 90 days'),
                'l_year': _t('Last 365 days'),
                'ls_past_until_now': _t('Past Till Now'),
                'ls_pastwithout_now': _t('Past Excluding Today'),
                'n_future_starting_now': _t('Future Starting Now'),
                'n_futurestarting_tomorrow': _t('Future Starting Tomorrow'),
                'l_custom': _t('Custom Filter'),
            };
            // To make sure date filter show date in specific order.
            this.tele_date_filter_selection_order = ['l_day', 't_week', 't_month', 't_quarter', 't_year', 'n_day',
                'n_week', 'n_month', 'n_quarter', 'n_year', 'ls_day', 'ls_week', 'ls_month', 'ls_quarter',
                'ls_year', 'l_week', 'l_month', 'l_quarter', 'l_year','ls_past_until_now', 'ls_pastwithout_now',
                 'n_future_starting_now', 'n_futurestarting_tomorrow', 'l_custom'
            ];

            this.tele_dashboard_id = state.params.tele_dashboard_id;

            this.gridstack_options = {
                staticGrid:true,
                float: false,
                cellHeight: 80,
                styleInHead : true,
//                disableOneColumnMode: true,

            };
            if (config.device.isMobileDevice) {
                this.gridstack_options.disableOneColumnMode = false
            }
            this.gridstackConfig = {};
            this.grid = false;
            this.chartMeasure = {};
            this.chart_container = {};
            this.list_container = {};


            this.teleChartColorOptions = ['default', 'cool', 'warm', 'neon'];
            this.teleUpdateDashboardItem = this.teleUpdateDashboardItem.bind(this);


            this.teleDateFilterSelection = false;
            this.teleDateFilterStartDate = false;
            this.teleDateFilterEndDate = false;
            this.teleUpdateDashboard = {};
            $("head").append('<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">');
            if(state.context.tele_reload_menu){
                this.trigger_up('reload_menu_data', { keep_open: true, scroll_to_bottom: true});
            }
        },

        getContext: function() {
            var self = this;
            var context = {
                teleDateFilterSelection: self.teleDateFilterSelection,
                teleDateFilterStartDate: self.teleDateFilterStartDate,
                teleDateFilterEndDate: self.teleDateFilterEndDate,
            }
            return Object.assign(context, session.user_context);
        },

        on_attach_callback: function() {
            var self = this;
            $.when(self.tele_fetch_items_data()).then(function(result){
                self.teleRenderDashboard();
                self.tele_set_update_interval();
                if (self.tele_dashboard_data.tele_item_data) {
                    self._teleSaveCurrentLayout();
                    session.user_context['gridstack_config'] = self.tele_get_current_gridstack_config();
                }
            });
        },

        tele_set_update_interval: function() {
            var self = this;
            if (self.tele_dashboard_data.tele_item_data) {

                Object.keys(self.tele_dashboard_data.tele_item_data).forEach(function(item_id) {
                    var item_data = self.tele_dashboard_data.tele_item_data[item_id]
                    var updateValue = self.tele_dashboard_data.tele_set_interval;
                    if (updateValue) {
                        if (!(item_id in self.teleUpdateDashboard)) {
                            if (['tele_tile', 'tele_list_view', 'tele_kpi', 'tele_to_do'].indexOf(item_data['tele_dashboard_item_type']) >= 0) {
                                var teleItemUpdateInterval = setInterval(function() {
                                    self.teleFetchUpdateItem(item_id)
                                }, updateValue);
                            } else {
                                var teleItemUpdateInterval = setInterval(function() {
                                    self.teleFetchChartItem(item_id)
                                }, updateValue);
                            }
                            self.teleUpdateDashboard[item_id] = teleItemUpdateInterval;
                        }
                    }
                });
            }
        },


        on_detach_callback: function() {
            var self = this;
            self.tele_remove_update_interval();
            if (self.teleDashboardEditMode) self._teleSaveCurrentLayout();

            self.teleDateFilterSelection = false;
            self.teleDateFilterStartDate = false;
            self.teleDateFilterEndDate = false;
//            self.tele_fetch_data();
        },

        tele_remove_update_interval: function() {
            var self = this;
            if (self.teleUpdateDashboard) {
                Object.values(self.teleUpdateDashboard).forEach(function(itemInterval) {
                    clearInterval(itemInterval);
                });
                self.teleUpdateDashboard = {};
            }
        },


        events: {
            'click #tele_add_item_selection > li': 'onAddItemTypeClick',
            'click .tele_dashboard_add_layout': '_onTeleAddLayoutClick',
            'click .tele_dashboard_edit_layout': '_onTeleEditLayoutClick',
            'click .tele_dashboard_select_item': 'onTeleSelectItemClick',
            'click .tele_dashboard_save_layout': '_onTeleSaveLayoutClick',
            'click .tele_dashboard_create_new_layout': '_onTeleCreateLayoutClick',
            'click .tele_dashboard_cancel_layout': '_onTeleCancelLayoutClick',
            'click .tele_item_click': '_onTeleItemClick',
            'click .tele_load_previous': 'teleLoadPreviousRecords',
            'click .tele_load_next': 'teleLoadMoreRecords',
            //            'click .tele_dashboard_item_action': '_onTeleItemActionClick',
            'click .tele_dashboard_item_customize': '_onTeleItemCustomizeClick',
            'click .tele_dashboard_item_delete': '_onTeleDeleteItemClick',
            'change .tele_dashboard_header_name': '_onTeleInputChange',
            'click .tele_duplicate_item': 'onTeleDuplicateItemClick',
            'click .tele_move_item': 'onTeleMoveItemClick',
            'change .tele_input_import_item_button': 'teleImportItem',
            'click .tele_dashboard_menu_container': function(e) {
                e.stopPropagation();
            },
            'click .tele_qe_dropdown_menu': function(e) {
                e.stopPropagation();
            },
            'click .tele_chart_json_export': 'teleItemExportJson',
            'click .tele_dashboard_item_action': 'teleStopClickPropagation',
            'show.bs.dropdown .tele_dropdown_container': 'onTeleDashboardMenuContainerShow',
            'hide.bs.dropdown .tele_dashboard_item_button_container': 'onTeleDashboardMenuContainerHide',

            //  Dn Filters Events
            'click .apply-dashboard-date-filter': '_onTeleApplyDateFilter',
            'click .clear-dashboard-date-filter': '_onTeleClearDateValues',
            'change #tele_start_date_picker': '_teleShowApplyClearDateButton',
            'change #tele_end_date_picker': '_teleShowApplyClearDateButton',
            'click .tele_date_filters_menu': '_teleOnDateFilterMenuSelect',
            'click #tele_item_info': 'teleOnListItemInfoClick',
            'click .tele_chart_color_options': 'teleRenderChartColorOptions',
            'click #tele_chart_canvas_id': 'onChartCanvasClick',
            'click .tele_list_canvas_click': 'onChartCanvasClick',
            'click .tele_dashboard_item_chart_info': 'onChartMoreInfoClick',
            'click .tele_chart_xls_csv_export': 'teleChartExportXlsCsv',
            'click .tele_chart_pdf_export': 'teleChartExportPdf',

            'click .tele_dashboard_quick_edit_action_popup': 'teleOnQuickEditView',
            'click .tele_dashboard_item_drill_up': 'teleOnDrillUp',

            'click .tele_dashboard_layout_event': '_teleOnDnLayoutMenuSelect',
            'click .tele_dashboard_set_current_layout': '_teleSetCurrentLayoutClick',
            'click .tele_dashboard_cancel_current_layout': '_teleSetDiscardCurrentLayoutClick',
            'click .tele_add_dashboard_item_on_empty' : 'tele_add_dashboard_item_on_empty',
            'click #dashboard_settings': 'teleOnDashboardSettingClick',
            'click #dashboard_delete': 'teleOnDashboardDeleteClick',
            'click #dashboard_create': 'teleOnDashboardCreateClick',
            'click #dashboard_export': 'teleOnDashboardExportClick',
            'click #dashboard_import': 'teleOnDashboardImportClick',
            'click #dashboard_duplicate': 'teleOnDashboardDuplicateClick',
        },

        teleOnDashboardDuplicateClick: function(ev){
         ev.preventDefault();
            var dashboard_id = this.tele_dashboard_id;
            var self= this;
            this._rpc({
                model: 'tele.dashboard.duplicate.wizard',
                method: "DuplicateDashBoard",
                args: [self.tele_dashboard_id],
                }).then((result)=>{
                    self.do_action(result)
                });
        },

        teleOnDashboardImportClick: function(ev){
         ev.preventDefault();
            var self = this;
            var dashboard_id = this.tele_dashboard_id;
            this._rpc({
                    model: 'tele_dashboard_ninja.board',
                    method: 'tele_open_import',
                    args: [dashboard_id],
                    kwargs: {
                        dashboard_id: dashboard_id
                    }
                    }).then((result)=>{
                    self.do_action(result)
                    });
        },

        teleOnDashboardExportClick: function(ev){
         ev.preventDefault();
           var self= this;
           var dashboard_id = JSON.stringify(this.tele_dashboard_id);
                this._rpc({
                model: 'tele_dashboard_ninja.board',
                method: "tele_dashboard_export",
                args: [dashboard_id],
                kwargs: {
                        dashboard_id: dashboard_id
                    }
            }).then(function(result) {
                var name = "dashboard_ninja";
                var data = {
                    "header": name,
                    "dashboard_data": result,
                }
                framework.blockUI();
                self.getSession().get_file({
                    url: '/tele_dashboard_ninja/export/dashboard_json',
                    data: {
                        data: JSON.stringify(data)
                    },
                    complete: framework.unblockUI,
                    error: (error) => this.call('crash_manager', 'rpc_error', error),
                });
            });
        },

        teleOnDashboardSettingClick: function(ev){
         ev.preventDefault();
            var self = this;
            var dashboard_id = this.tele_dashboard_id;
            this._rpc({
                    model: 'tele_dashboard_ninja.board',
                    method: 'tele_open_setting',
                    args: [dashboard_id],
                    kwargs: {
                        dashboard_id: dashboard_id
                    }
                    }).then((result)=>{
                    self.do_action(result)
                    });
        },

        teleOnDashboardDeleteClick: function(ev){
         ev.preventDefault();
           var dashboard_id = this.tele_dashboard_id;
           var self= this;
                this._rpc({
                model: 'tele.dashboard.delete.wizard',
                method: "DeleteDashBoard",
                args: [self.tele_dashboard_id],
            }).then((result)=>{
                    self.do_action(result);
              });
        },

        teleOnDashboardCreateClick: function(ev){
           var self= this;
//                this._rpc({
//                model: 'tele.dashboard.wizard',
//                method: "CreateDashBoard",
//                args: [''],
//            }).then((result)=>{
//                self.do_action(result);
//              });
           var action = {
                name: _t('Create Dashboard'),
                type: 'ir.actions.act_window',
                res_model: 'tele.dashboard.wizard',
                domain: [],
                context: {
                },
                views: [
                    [false, 'form']
                ],
                view_mode: 'form',
                target: 'new',
           }
           self.do_action(action)

        },


        _teleOnDnLayoutMenuSelect: function(ev){
            var selected_layout_id = $(ev.currentTarget).data('tele_layout_id');
            this.teleOnLayoutSelection(selected_layout_id);

        },

        teleOnLayoutSelection: function(layout_id){
            var self = this;
            var selected_layout_name = this.tele_dashboard_data.tele_child_boards[layout_id][0];
            var selected_layout_grid_config = this.tele_dashboard_data.tele_child_boards[layout_id][1];
            this.gridstackConfig = JSON.parse(selected_layout_grid_config);
            _(this.gridstackConfig).each((x,y)=>{
                self.grid.update(self.$el.find(".grid-stack-item[gs-id=" + y + "]")[0],{ x:x['x'], y:x['y'], w:x['w'], h:x['h'],autoPosition:false});
            });


//            this.tele_dashboard_data.tele_selected_board_id = layout_id;
            this.$el.find("#tele_dashboard_layout_dropdown_container .tele_layout_selected").removeClass("tele_layout_selected");
            this.$el.find("li.tele_dashboard_layout_event[data-tele_layout_id='"+ layout_id + "']").addClass('tele_layout_selected');
            this.$el.find("#tele_dn_layout_button span:first-child").text(selected_layout_name);
            this.$el.find(".tele_dashboard_top_menu .tele_dashboard_top_settings").addClass("tele_hide");
            this.$el.find(".tele_dashboard_top_menu .tele_am_content_element").addClass("tele_hide");
            this.$el.find(".tele_dashboard_layout_edit_mode_settings").removeClass("tele_hide");
        },

        _teleSetCurrentLayoutClick: function(){
            var self = this;
            this.tele_dashboard_data.tele_selected_board_id = this.$el.find("#tele_dashboard_layout_dropdown_container .tele_layout_selected").data('tele_layout_id');
            this.$el.find(".tele_dashboard_top_menu .tele_dashboard_top_settings").removeClass("tele_hide");
            this.$el.find(".tele_dashboard_top_menu .tele_am_content_element").removeClass("tele_hide");
            this.$el.find(".tele_dashboard_layout_edit_mode_settings").addClass("tele_hide");
//            $('#tele_dashboard_title_input').val(this.tele_dashboard_data.tele_child_boards[this.tele_dashboard_data.tele_selected_board_id][0]);
            this.tele_dashboard_data.name = this.tele_dashboard_data.tele_child_boards[this.tele_dashboard_data.tele_selected_board_id][0];

            this._rpc({
                model: 'tele_dashboard_ninja.board',
                method: 'update_child_board',
                args: ['update', self.tele_dashboard_id, {
                    "tele_selected_board_id": this.tele_dashboard_data.tele_selected_board_id,
                }],
            });
        },

        _teleSetDiscardCurrentLayoutClick: function(){
            this.teleOnLayoutSelection(this.tele_dashboard_data.tele_selected_board_id);
            this.$el.find(".tele_dashboard_top_menu .tele_dashboard_top_settings").removeClass("tele_hide");
            this.$el.find(".tele_dashboard_top_menu .tele_am_content_element").removeClass("tele_hide");
            this.$el.find(".tele_dashboard_layout_edit_mode_settings").addClass("tele_hide");

        },


        teleOnQuickEditView: function(e) {
            var self = this;
            var item_id = e.currentTarget.dataset.itemId;
            var item_data = this.tele_dashboard_data.tele_item_data[item_id];
            var item_el = $.find('[gs-id=' + item_id + ']');
            var $quickEditButton = $(QWeb.render('teleQuickEditButtonContainer', {
                grid: $.extend({}, item_el[0].gridstackNode)
            }));
            $(item_el).before($quickEditButton);

            var teleQuickEditViewWidget = new TeleQuickEditView.QuickEditView(this, {
                item: item_data,
            });

            teleQuickEditViewWidget.appendTo($quickEditButton.find('.dropdown-menu'));

            teleQuickEditViewWidget.on("canBeDestroyed", this, function(result) {
                if (teleQuickEditViewWidget) {
                    teleQuickEditViewWidget = false;
                    $quickEditButton.find('.tele_dashboard_item_action').click();
                }
            });

            teleQuickEditViewWidget.on("canBeRendered", this, function(result) {
                $quickEditButton.find('.tele_dashboard_item_action').click();
            });

            teleQuickEditViewWidget.on("openFullItemForm", this, function(result) {
                teleQuickEditViewWidget.destroy();
                $quickEditButton.find('.tele_dashboard_item_action').click();
                self.tele_open_item_form_page(parseInt(item_id));
            });


            $quickEditButton.on("hide.bs.dropdown", function(ev) {
                if (ev.hasOwnProperty("clickEvent") && document.contains(ev.clickEvent.target)) {
                    if (teleQuickEditViewWidget) {
                        teleQuickEditViewWidget.teleDiscardChanges();
                        teleQuickEditViewWidget = false;
                        self.tele_set_update_interval();
                        $quickEditButton.remove();
                    } else {
                        self.tele_set_update_interval();
                        $quickEditButton.remove();
                    }
                } else if (!ev.hasOwnProperty("clickEvent")) {
                    self.tele_set_update_interval();
                    $quickEditButton.remove();
                } else {
                    return false;
                }
            });

            $quickEditButton.on("show.bs.dropdown", function() {
                self.tele_remove_update_interval();
            });

            e.stopPropagation();
        },

        willStart: function() {
            var self = this;
            var def;
            if (this.reload_menu_option.reload && this.reload_menu_option.menu_id) {
                def = this.getParent().actionService.teleDnReloadMenu(this.reload_menu_option.menu_id);
            }
            return $.when(def, ajax.loadLibs(this), this._super()).then(function() {
                return self.tele_fetch_data();
            });
        },

        start: function() {
            var self = this;
            self.tele_set_default_chart_view();
            return this._super()
        },

        tele_set_default_chart_view: function() {
            Chart.plugins.unregister(ChartDataLabels);
            var backgroundColor = 'white';
            Chart.plugins.register({
                beforeDraw: function(c) {
                    var ctx = c.chart.ctx;
                    ctx.fillStyle = backgroundColor;
                    ctx.fillRect(0, 0, c.chart.width, c.chart.height);
                }
            });
            Chart.plugins.register({
                afterDraw: function(chart) {
                    if (chart.data.labels.length === 0) {
                        // No data is present
                        var ctx = chart.chart.ctx;
                        var width = chart.chart.width;
                        var height = chart.chart.height
                        chart.clear();

                        ctx.save();
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.font = "3rem 'Lucida Grande'";
                        ctx.fillText('No data available', width / 2, height / 2);
                        ctx.restore();
                    }
                }

            });

            Chart.Legend.prototype.afterFit = function() {
                var chart_type = this.chart.config.type;
                if (chart_type === "pie" || chart_type === "doughnut") {
                    this.height = this.height;
                } else {
                    this.height = this.height + 20;
                };
            };
        },

        teleFetchUpdateItem: function(item_id) {
            var self = this;
            return self._rpc({
                model: 'tele_dashboard_ninja.board',
                method: 'tele_fetch_item',
                args: [
                    [parseInt(item_id)], self.tele_dashboard_id, self.teleGetParamsForItemFetch(parseInt(item_id))
                ],
                context: self.getContext(),
            }).then(function(new_item_data) {
                this.tele_dashboard_data.tele_item_data[item_id] = new_item_data[item_id];
                this.teleUpdateDashboardItem([item_id]);
            }.bind(this));
        },

        teleRenderChartColorOptions: function(e) {
            var self = this;
            if (!$(e.currentTarget).parent().hasClass('tele_date_filter_selected')) {
                //            FIXME : Correct this later.
                var $parent = $(e.currentTarget).parent().parent();
                $parent.find('.tele_date_filter_selected').removeClass('tele_date_filter_selected')
                $(e.currentTarget).parent().addClass('tele_date_filter_selected')
                var item_data = self.tele_dashboard_data.tele_item_data[$parent.data().itemId];
                var chart_data = JSON.parse(item_data.tele_chart_data);
                this.teleChartColors(e.currentTarget.dataset.chartColor, this.chart_container[$parent.data().itemId], $parent.data().chartType, $parent.data().chartFamily, item_data.tele_bar_chart_stacked, item_data.tele_semi_circle_chart, item_data.tele_show_data_value, chart_data, item_data)
                this._rpc({
                    model: 'tele_dashboard_ninja.item',
                    method: 'write',
                    args: [$parent.data().itemId, {
                        "tele_chart_item_color": e.currentTarget.dataset.chartColor
                    }],
                }).then(function() {
                    self.tele_dashboard_data.tele_item_data[$parent.data().itemId]['tele_chart_item_color'] = e.currentTarget.dataset.chartColor;
                });
            }
        },

        //To fetch dashboard data.
        tele_fetch_data: function() {
            var self = this;
            return this._rpc({
                model: 'tele_dashboard_ninja.board',
                method: 'tele_fetch_dashboard_data',
                args: [self.tele_dashboard_id],
                context: self.getContext(),
            }).then(function(result) {
//                result = self.normalize_dn_data(result);
                self.tele_dashboard_data = result;
            });
        },

        normalize_dn_data: function(result){
            _(result.tele_child_boards).each((x,y)=>{if (typeof(y)==='number'){
                result[y.toString()] = result[y];
                delete result[y];
            }})
            return result;
        },

        tele_fetch_items_data: function(){
            var self = this;
            var items_promises = []
            self.tele_dashboard_data.tele_dashboard_items_ids.forEach(function(item_id){
                items_promises.push(self._rpc({
                    model: "tele_dashboard_ninja.board",
                    method: "tele_fetch_item",
                    context: self.getContext(),
                    args : [[item_id], self.tele_dashboard_id, self.teleGetParamsForItemFetch(item_id)]
                }).then(function(result){
                    self.tele_dashboard_data.tele_item_data[item_id] = result[item_id];
                }));
            });

            return Promise.all(items_promises)
        },

        teleGetParamsForItemFetch: function(){
            return {};
        },

        on_reverse_breadcrumb: function(state) {
            var self = this;
            self.trigger_up('push_state', {
                controllerID: this.controllerID,
                state: state || {},
            });
            return $.when(self.tele_fetch_data());
        },

        teleStopClickPropagation: function(e) {
            this.teleAllowItemClick = false;
        },

        onTeleDashboardMenuContainerShow: function(e) {
            $(e.currentTarget).addClass('tele_dashboard_item_menu_show');
            var item_id = e.currentTarget.dataset.item_id;
            if (this.teleUpdateDashboard[item_id]){
                clearInterval(this.teleUpdateDashboard[item_id]);
                delete this.teleUpdateDashboard[item_id]
            }

            //            Dynamic Bootstrap menu populate Image Report
            if ($(e.target).hasClass('tele_dashboard_more_action')) {
                var chart_id = e.target.dataset.itemId;
                var name = this.tele_dashboard_data.tele_item_data[chart_id].name;
                var base64_image = this.chart_container[chart_id].toBase64Image();
                $(e.target).find('.dropdown-menu').empty();
                $(e.target).find('.dropdown-menu').append($(QWeb.render('teleMoreChartOptions', {
                    href: base64_image,
                    download_fileName: name,
                    chart_id: chart_id
                })))
            }
        },

        onTeleDashboardMenuContainerHide: function(e) {
            var self = this;
            $(e.currentTarget).removeClass('tele_dashboard_item_menu_show');
            var item_id = e.currentTarget.dataset.item_id;
            var updateValue = self.tele_dashboard_data.tele_set_interval;
            if (updateValue) {
                var updateinterval = setInterval(function() {
                    self.teleFetchUpdateItem(item_id)
                }, updateValue);
                self.teleUpdateDashboard[item_id] = updateinterval;
            }
            if (this.tele_dashboard_data.tele_item_data[item_id]['isDrill'] == true) {
                clearInterval(this.teleUpdateDashboard[item_id]);
            }
        },

        tele_get_dark_color: function(color, opacity, percent) {
            var num = parseInt(color.slice(1), 16),
                amt = Math.round(2.55 * percent),
                R = (num >> 16) + amt,
                G = (num >> 8 & 0x00FF) + amt,
                B = (num & 0x0000FF) + amt;
            return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1) + "," + opacity;
        },


        //    This is to convert color #value into RGB format to add opacity value.
        _tele_get_rgba_format: function(val) {
            var rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
            rgba = rgba.map(function(v) {
                return parseInt(v, 16)
            }).join(",");
            return "rgba(" + rgba + "," + val.split(',')[1] + ")";
        },

        teleRenderDashboard: function() {
            var self = this;
            self.$el.empty();
            self.$el.addClass('tele_dashboard_ninja d-flex flex-column');
            var dash_name = $('ul[id="tele_dashboard_layout_dropdown_container"] li[class="tele_dashboard_layout_event tele_layout_selected"] span').text()
            if (self.tele_dashboard_data.tele_child_boards) self.tele_dashboard_data.name = this.tele_dashboard_data.tele_child_boards[self.tele_dashboard_data.tele_selected_board_id][0];
            var $tele_header = $(QWeb.render('teleDashboardNinjaHeader', {
                tele_dashboard_name: self.tele_dashboard_data.name,
                tele_multi_layout: self.tele_dashboard_data.multi_layouts,
                tele_dash_name: self.tele_dashboard_data.name,
                tele_dashboard_manager: self.tele_dashboard_data.tele_dashboard_manager,
                date_selection_data: self.tele_date_filter_selections,
                date_selection_order: self.tele_date_filter_selection_order,
                tele_show_create_layout_option: (Object.keys(self.tele_dashboard_data.tele_item_data).length > 0) && self.tele_dashboard_data.tele_dashboard_manager,
                tele_show_layout: self.tele_dashboard_data.tele_dashboard_manager && self.tele_dashboard_data.tele_child_boards && true,
                tele_selected_board_id: self.tele_dashboard_data.tele_selected_board_id,
                tele_child_boards: self.tele_dashboard_data.tele_child_boards,
                tele_dashboard_data: self.tele_dashboard_data,
                tele_dn_pre_defined_filters: _(self.tele_dashboard_data.tele_dashboard_pre_domain_filter).values().sort(function(a, b){return a.sequence - b.sequence}),
            }));

            if (!config.device.isMobile) {
                $tele_header.addClass("tele_dashboard_header_sticky")
            }

            self.$el.append($tele_header);
            if (Object.keys(self.tele_dashboard_data.tele_item_data).length===0){
                self.$el.find('.tele_dashboard_link').addClass("d-none");
                self.$el.find('.tele_dashboard_edit_layout').addClass("d-none");
            }
            self.teleRenderDashboardMainContent();
            if (Object.keys(self.tele_dashboard_data.tele_item_data).length === 0) {
                self._teleRenderNoItemView();
            }
        },

        teleRenderDashboardMainContent: function() {
            var self = this;
            if (config.device.isMobile && $('#tele_dn_layout_button :first-child').length > 0) {
                $('.tele_am_element').append($('#tele_dn_layout_button :first-child')[0].innerText);
                this.$el.find("#tele_dn_layout_button").addClass("tele_hide");
            }
            if (self.tele_dashboard_data.tele_item_data) {
                self._renderDateFilterDatePicker();

                self.$el.find('.tele_dashboard_link').removeClass("tele_hide");

                $('.tele_dashboard_items_list').remove();
                var $dashboard_body_container = $(QWeb.render('tele_main_body_container'))
                var $gridstackContainer = $dashboard_body_container.find(".grid-stack");
                $dashboard_body_container.appendTo(self.$el)
                self.grid = GridStack.init(self.gridstack_options,$gridstackContainer[0]);
                var items = self.teleSortItems(self.tele_dashboard_data.tele_item_data);

                self.teleRenderDashboardItems(items);

                // In gridstack version 0.3 we have to make static after adding element in dom
                self.grid.setStatic(true);

            } else if (!self.tele_dashboard_data.tele_item_data) {
                self.$el.find('.tele_dashboard_link').addClass("tele_hide");
                self._teleRenderNoItemView();
            }
        },

        // This function is for maintaining the order of items in mobile view
        teleSortItems: function(tele_item_data) {
            var items = []
            var self = this;
            var item_data = Object.assign({}, tele_item_data);
            if (self.tele_dashboard_data.tele_gridstack_config) {
                self.gridstackConfig = JSON.parse(self.tele_dashboard_data.tele_gridstack_config);
                var a = Object.values(self.gridstackConfig);
                var b = Object.keys(self.gridstackConfig);
                for (var i = 0; i < a.length; i++) {
                    a[i]['id'] = b[i];
                }
                a.sort(function(a, b) {
                    return (35 * a.y + a.x) - (35 * b.y + b.x);
                });
                for (var i = 0; i < a.length; i++) {
                    if (item_data[a[i]['id']]) {
                        items.push(item_data[a[i]['id']]);
                        delete item_data[a[i]['id']];
                    }
                }
            }

            return items.concat(Object.values(item_data));
        },

        teleRenderDashboardItems: function(items) {
            var self = this;
            self.$el.find('.print-dashboard-btn').addClass("tele_pro_print_hide");
            if (self.tele_dashboard_data.tele_gridstack_config) {
                self.gridstackConfig = JSON.parse(self.tele_dashboard_data.tele_gridstack_config);
            }
            var item_view;
            var tele_container_class = 'grid-stack-item',
                tele_inner_container_class = 'grid-stack-item-content';
                for (var i = 0; i < items.length; i++) {
                if (self.grid) {

                    if (items[i].tele_dashboard_item_type === 'tele_tile') {
                        var item_view = self._teleRenderDashboardTile(items[i])
                        if (items[i].id in self.gridstackConfig) {
//                            self.grid.addWidget($(item_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 2, items[i].id);
                             self.grid.addWidget($(item_view)[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:true,minW:2,maxW:null,minH:2,maxH:null,id:items[i].id});
                        } else {
                             self.grid.addWidget($(item_view)[0], {x:0, y:0, w:4, h:2,autoPosition:true,minW:2,maxW:null,minH:2,maxH:2,id:items[i].id});
                        }
                    } else if (items[i].tele_dashboard_item_type === 'tele_list_view') {
                        self._renderListView(items[i], self.grid)
                    }else if (items[i].tele_dashboard_item_type === 'tele_kpi') {
                        var kpi_preview = self.renderKpi(items[i], self.grid)
                        if (items[i].id in self.gridstackConfig) {
                            self.grid.addWidget($kpi_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:true,minW:2,maxW:null,minH:2,maxH:null,id:items[i].id});
                        } else {
                             self.grid.addWidget($kpi_preview[0], {x:0, y:0, w:3, h:2,autoPosition:true,minW:2,maxW:null,minH:2,maxH:null,id:items[i].id});
                        }

                    }else {
                        self._renderGraph(items[i], self.grid)
                    }
                }
            }
        },

        _teleRenderDashboardTile: function(tile) {
            var self = this;
            var tele_container_class = 'grid-stack-item';
            var tele_inner_container_class = 'grid-stack-item-content';
            var tele_icon_url, item_view;
            var tele_rgba_background_color, tele_rgba_font_color, tele_rgba_default_icon_color,tele_rgba_button_color;
            var style_main_body, style_image_body_l2, style_domain_count_body, style_button_customize_body,
                style_button_delete_body;


            if (tile.tele_multiplier_active){
                var tele_record_count = tile.tele_record_count * tile.tele_multiplier
                var data_count = TeleGlobalFunction._onTeleGlobalFormatter(tele_record_count, tile.tele_data_formatting, tile.tele_precision_digits);
                var count = tele_record_count;
            }else{
                 var data_count = TeleGlobalFunction._onTeleGlobalFormatter(tile.tele_record_count, tile.tele_data_formatting, tile.tele_precision_digits);
                 var count = tele_record_count
            }
            if (tile.tele_icon_select == "Custom") {
                if (tile.tele_icon[0]) {
                    tele_icon_url = 'data:image/' + (self.file_type_magic_word[tile.tele_icon[0]] || 'png') + ';base64,' + tile.tele_icon;
                } else {
                    tele_icon_url = false;
                }
            }


            tile.teleIsDashboardManager = self.tele_dashboard_data.tele_dashboard_manager;
            tile.teleIsUser = true;
            tele_rgba_background_color = self._tele_get_rgba_format(tile.tele_background_color);
            tele_rgba_font_color = self._tele_get_rgba_format(tile.tele_font_color);
            tele_rgba_default_icon_color = self._tele_get_rgba_format(tile.tele_default_icon_color);
            tele_rgba_button_color = self._tele_get_rgba_format(tile.tele_button_color);
            style_main_body = "background-color:" + tele_rgba_background_color + ";color : " + tele_rgba_font_color + ";";
            switch (tile.tele_layout) {
                case 'layout1':
                    item_view = QWeb.render('tele_dashboard_item_layout1', {
                        item: tile,
                        style_main_body: style_main_body,
                        tele_icon_url: tele_icon_url,
                        tele_rgba_default_icon_color: tele_rgba_default_icon_color,
                        tele_rgba_button_color:tele_rgba_button_color,
                        tele_container_class: tele_container_class,
                        tele_inner_container_class: tele_inner_container_class,
                        tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                        data_count: data_count,
                        count: count
                    });
                    break;

                case 'layout2':
                    var tele_rgba_dark_background_color_l2 = self._tele_get_rgba_format(self.tele_get_dark_color(tile.tele_background_color.split(',')[0], tile.tele_background_color.split(',')[1], -10));
                    style_image_body_l2 = "background-color:" + tele_rgba_dark_background_color_l2 + ";";
                    item_view = QWeb.render('tele_dashboard_item_layout2', {
                        item: tile,
                        style_image_body_l2: style_image_body_l2,
                        style_main_body: style_main_body,
                        tele_icon_url: tele_icon_url,
                        tele_rgba_default_icon_color: tele_rgba_default_icon_color,
                        tele_rgba_button_color:tele_rgba_button_color,
                        tele_container_class: tele_container_class,
                        tele_inner_container_class: tele_inner_container_class,
                        tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                        data_count: data_count,
                        count: count

                    });
                    break;

                case 'layout3':
                    item_view = QWeb.render('tele_dashboard_item_layout3', {
                        item: tile,
                        style_main_body: style_main_body,
                        tele_icon_url: tele_icon_url,
                        tele_rgba_default_icon_color: tele_rgba_default_icon_color,
                        tele_rgba_button_color:tele_rgba_button_color,
                        tele_container_class: tele_container_class,
                        tele_inner_container_class: tele_inner_container_class,
                        tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                        data_count: data_count,
                        count: count

                    });
                    break;

                case 'layout4':
                    style_main_body = "color : " + tele_rgba_font_color + ";border : solid;border-width : 1px;border-color:" + tele_rgba_background_color + ";"
                    style_image_body_l2 = "background-color:" + tele_rgba_background_color + ";";
                    style_domain_count_body = "color:" + tele_rgba_background_color + ";";
                    item_view = QWeb.render('tele_dashboard_item_layout4', {
                        item: tile,
                        style_main_body: style_main_body,
                        style_image_body_l2: style_image_body_l2,
                        style_domain_count_body: style_domain_count_body,
                        tele_icon_url: tele_icon_url,
                        tele_rgba_default_icon_color: tele_rgba_default_icon_color,
                        tele_rgba_button_color:tele_rgba_button_color,
                        tele_container_class: tele_container_class,
                        tele_inner_container_class: tele_inner_container_class,
                        tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                        data_count: data_count,
                        count: count

                    });
                    break;

                case 'layout5':
                    item_view = QWeb.render('tele_dashboard_item_layout5', {
                        item: tile,
                        style_main_body: style_main_body,
                        tele_icon_url: tele_icon_url,
                        tele_rgba_default_icon_color: tele_rgba_default_icon_color,
                        tele_rgba_button_color:tele_rgba_button_color,
                        tele_container_class: tele_container_class,
                        tele_inner_container_class: tele_inner_container_class,
                        tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                        data_count: data_count,
                        count: count

                    });
                    break;

                case 'layout6':
                    tele_rgba_default_icon_color = self._tele_get_rgba_format(tile.tele_default_icon_color);
                    item_view = QWeb.render('tele_dashboard_item_layout6', {
                        item: tile,
                        style_image_body_l2: style_image_body_l2,
                        style_main_body: style_main_body,
                        tele_icon_url: tele_icon_url,
                        tele_rgba_default_icon_color: tele_rgba_default_icon_color,
                        tele_rgba_button_color:tele_rgba_button_color,
                        tele_container_class: tele_container_class,
                        tele_inner_container_class: tele_inner_container_class,
                        tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                        data_count: data_count,
                        count: count

                    });
                    break;

                default:
                    item_view = QWeb.render('tele_dashboard_item_layout_default', {
                        item: tile
                    });
                    break;
            }


            return item_view
        },

        _renderGraph: function(item) {
            var self = this;
            var chart_data = JSON.parse(item.tele_chart_data);
            var isDrill = item.isDrill ? item.isDrill : false;
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.tele_dashboard_item_type.split('_')[1];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;

            }

            var $tele_gridstack_container = $(QWeb.render('tele_gridstack_container', {
                tele_chart_title: chart_title,
                teleIsDashboardManager: self.tele_dashboard_data.tele_dashboard_manager,
                teleIsUser: true,
                tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                chart_id: chart_id,
                chart_family: chart_family,
                chart_type: chart_type,
                teleChartColorOptions: this.teleChartColorOptions,
            })).addClass('tele_dashboarditem_id');
            $tele_gridstack_container.find('.tele_li_' + item.tele_chart_item_color).addClass('tele_date_filter_selected');

            var teleLayoutGridId = $(self.$el[0]).find('.tele_layout_selected').attr('data-tele_layout_id')
            if(teleLayoutGridId && teleLayoutGridId != 'tele_default'){
                self.gridstackConfig = JSON.parse(self.tele_dashboard_data.tele_child_boards[parseInt(teleLayoutGridId)][1])
            }
            parseInt($(self.$el[0]).find('.tele_layout_selected').attr('data-tele_layout_id'))
            if (chart_id in self.gridstackConfig) {
                if (config.device.isMobile){
                    self.grid.addWidget($tele_gridstack_container[0], {x:self.gridstackConfig[chart_id].x, y:self.gridstackConfig[chart_id].y, w:self.gridstackConfig[chart_id].w, h:self.gridstackConfig[chart_id].h, autoPosition:true,minW:4,maxW:null,minH:3,maxH:null,id :chart_id});
                }
                else{
                    self.grid.addWidget($tele_gridstack_container[0], {x:self.gridstackConfig[chart_id].x, y:self.gridstackConfig[chart_id].y, w:self.gridstackConfig[chart_id].w, h:self.gridstackConfig[chart_id].h, autoPosition:false,minW:4,maxW:null,minH:3,maxH:null,id :chart_id});
                }
//                self.grid.addWidget($tele_gridstack_container, self.gridstackConfig[chart_id].x, self.gridstackConfig[chart_id].y, self.gridstackConfig[chart_id].width, self.gridstackConfig[chart_id].height, false, 11, null, 3, null, chart_id);
            } else {
//                self.grid.addWidget($tele_gridstack_container, 0, 0, 13, 4, true, 11, null, 3, null, chart_id);
                  self.grid.addWidget($tele_gridstack_container[0], {x:0, y:0, w:5, h:4,autoPosition:true,minW:4,maxW:null,minH:3,maxH:null, id :chart_id});
            }
            self._renderChart($tele_gridstack_container, item);
        },

        _renderChart: function($tele_gridstack_container, item) {
            var self = this;
            var chart_data = JSON.parse(item.tele_chart_data);

            if (item.tele_chart_cumulative_field){

                for (var i=0; i< chart_data.datasets.length; i++){
                    var tele_temp_com = 0
                    var data = []
                    var datasets = {}
                    if (chart_data.datasets[i].tele_chart_cumulative_field){
                        for (var j=0; j < chart_data.datasets[i].data.length; j++)
                            {
                                tele_temp_com = tele_temp_com + chart_data.datasets[i].data[j];
                                data.push(tele_temp_com);
                            }
                            datasets.label =  'Cumulative' + chart_data.datasets[i].label;
                            datasets.data = data;
                            if (item.tele_chart_cumulative){
                                datasets.type =  'line';
                            }
                            chart_data.datasets.push(datasets);
                    }
                }
            }
            if (item.tele_chart_is_cumulative && item.tele_chart_data_count_type == 'count' && item.tele_dashboard_item_type === 'tele_bar_chart'){
                var tele_temp_com = 0
                var data = []
                var datasets = {}
                for (var j=0; j < chart_data.datasets[0].data.length; j++){
                        tele_temp_com = tele_temp_com + chart_data.datasets[0].data[j];
                        data.push(tele_temp_com);
                    }
                datasets.label =  'Cumulative' + chart_data.datasets[0].label;
                datasets.data = data;
                if (item.tele_chart_cumulative){
                    datasets.type =  'line';
                }
                chart_data.datasets.push(datasets);
            }
            var isDrill = item.isDrill ? item.isDrill : false;
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.tele_dashboard_item_type.split('_')[1];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "horizontalBar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;

            }
            $tele_gridstack_container.find('.tele_color_pallate').data({
                chartType: chart_type,
                chartFamily: chart_family
            }); {
                chartType: "pie"
            }
            var $teleChartContainer = $('<canvas id="tele_chart_canvas_id" data-chart-id=' + chart_id + '/>');
            $tele_gridstack_container.find('.card-body').append($teleChartContainer);
            if (!item.tele_show_records) {
                $tele_gridstack_container.find('.tele_dashboard_item_chart_info').hide();
            }
            item.$el = $tele_gridstack_container;
            if (chart_family === "circle") {
                if (chart_data && chart_data['labels'].length > 30) {
                    $tele_gridstack_container.find(".tele_dashboard_color_option").remove();
                    $tele_gridstack_container.find(".card-body").empty().append($("<div style='font-size:20px;'>Too many records for selected Chart Type. Consider using <strong>Domain</strong> to filter records or <strong>Record Limit</strong> to limit the no of records under <strong>30.</strong>"));
                    return;
                }
            }

            if (chart_data["tele_show_second_y_scale"] && item.tele_dashboard_item_type === 'tele_bar_chart') {
                var scales = {}
                scales.yAxes = [{
                        type: "linear",
                        display: true,
                        position: "left",
                        id: "y-axis-0",
                        gridLines: {
                            display: true
                        },
                        labels: {
                            show: true,
                        }
                    },
                    {
                        type: "linear",
                        display: true,
                        position: "right",
                        id: "y-axis-1",
                        labels: {
                            show: true,
                        },
                        ticks: {
                            beginAtZero: true,
                            callback: function(value, index, values) {
                                var tele_selection = chart_data.tele_selection;
                                if (tele_selection === 'monetary') {
                                    var tele_currency_id = chart_data.tele_currency;
                                    var tele_data = value;
                                    tele_data = TeleGlobalFunction._onTeleGlobalFormatter(tele_data, item.tele_data_formatting, item.tele_precision_digits);
                                    tele_data = TeleGlobalFunction.tele_monetary(tele_data, tele_currency_id);
                                   return tele_data;
                                } else if (tele_selection === 'custom') {
                                    var tele_field = chart_data.tele_field;
                                    return TeleGlobalFunction._onTeleGlobalFormatter(value, item.tele_data_formatting, item.tele_precision_digits) + ' ' + tele_field;

                                } else {
                                   return TeleGlobalFunction._onTeleGlobalFormatter(value, item.tele_data_formatting, item.tele_precision_digits);
                                }
                            },
                        }
                    }
                ]
            }
            var chart_plugin = [];
            if (item.tele_show_data_value) {
                chart_plugin.push(ChartDataLabels);
            }
            if (item.tele_data_label_type == 'value'){
                chart_data.datasets[0]["tele_data_label_type"] = 'value';
            }
            var teleMyChart = new Chart($teleChartContainer[0], {
                type: chart_type === "area" ? "line" : chart_type,
                plugins: chart_plugin,
                data: {
                    labels: chart_data['labels'],
                    groupByIds: chart_data['groupByIds'],
                    domains: chart_data['domains'],
                    datasets: chart_data.datasets,
                },
                options: {
                    maintainAspectRatio: false,
                    responsiveAnimationDuration: 1000,
                    animation: {
                        easing: 'easeInQuad',
                    },
                   legend: {
                            display: item.tele_hide_legend
                        },
                    scales: scales,
                   layout: {
                        padding: {
                        bottom: 0,
                   }
                },
                plugins: {
                    datalabels: {
                        backgroundColor: function(context) {
                            return context.dataset.backgroundColor;
                        },
                        borderRadius: 4,
                        color: 'white',
                        font: {
                            weight: 'bold'
                        },
                        anchor: 'right',
                        textAlign: 'center',
                        display: 'auto',
                        clamp: true,
                        formatter: function(value, ctx) {
                            let sum = 0;
                            let dataArr = ctx.dataset.data;
                            dataArr.map(data => {
                                sum += data;
                            });
                            let percentage = sum === 0 ? 0 + "%" : (value * 100 / sum).toFixed(2) + "%";
                            if (ctx.dataset.tele_data_label_type == 'value'){
                                percentage = value;
                            }
                            return percentage;
                        },
                    },
                },

                }
            });

            this.chart_container[chart_id] = teleMyChart;
            if (chart_data && chart_data["datasets"].length > 0) self.teleChartColors(item.tele_chart_item_color, teleMyChart, chart_type, chart_family, item.tele_bar_chart_stacked, item.tele_semi_circle_chart, item.tele_show_data_value, chart_data, item);

        },

        teleHideFunction: function(options, item, teleChartFamily, chartType) {
            return options;
        },

        teleChartColors: function(palette, teleMyChart, teleChartType, teleChartFamily, stack, semi_circle, tele_show_data_value, chart_data, item) {
            chart_data;
            var self = this;
            var currentPalette = "cool";
            if (!palette) palette = currentPalette;
            currentPalette = palette;

            /*Gradients
              The keys are percentage and the values are the color in a rgba format.
              You can have as many "color stops" (%) as you like.
              0% and 100% is not optional.*/
            var gradient;
            switch (palette) {
                case 'cool':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [220, 237, 200, 1],
                        45: [66, 179, 213, 1],
                        65: [26, 39, 62, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'warm':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [254, 235, 101, 1],
                        45: [228, 82, 27, 1],
                        65: [77, 52, 47, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'neon':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [255, 236, 179, 1],
                        45: [232, 82, 133, 1],
                        65: [106, 27, 154, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;

                case 'default':
                    var color_set = ['#F04F65', '#f69032', '#fdc233', '#53cfce', '#36a2ec', '#8a79fd', '#b1b5be', '#1c425c', '#8c2620', '#71ecef', '#0b4295', '#f2e6ce', '#1379e7']
            }

            //Find datasets and length
            var chartType = teleMyChart.config.type;
            switch (chartType) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    if (teleMyChart.config.data.datasets[0]){
                        var datasets = teleMyChart.config.data.datasets[0];
                        var setsCount = datasets.data.length;
                    }
                    break;

                case "bar":
                case "horizontalBar":
                case "line":
                    if (teleMyChart.config.data.datasets[0]){
                        var datasets = teleMyChart.config.data.datasets;
                        var setsCount = datasets.length;
                    }
                    break;
            }

            //Calculate colors
            var chartColors = [];

            if (palette !== "default") {
                //Get a sorted array of the gradient keys
                var gradientKeys = Object.keys(gradient);
                gradientKeys.sort(function(a, b) {
                    return +a - +b;
                });
                for (var i = 0; i < setsCount; i++) {
                    var gradientIndex = (i + 1) * (100 / (setsCount + 1)); //Find where to get a color from the gradient
                    for (var j = 0; j < gradientKeys.length; j++) {
                        var gradientKey = gradientKeys[j];
                        if (gradientIndex === +gradientKey) { //Exact match with a gradient key - just get that color
                            chartColors[i] = 'rgba(' + gradient[gradientKey].toString() + ')';
                            break;
                        } else if (gradientIndex < +gradientKey) { //It's somewhere between this gradient key and the previous
                            var prevKey = gradientKeys[j - 1];
                            var gradientPartIndex = (gradientIndex - prevKey) / (gradientKey - prevKey); //Calculate where
                            var color = [];
                            for (var k = 0; k < 4; k++) { //Loop through Red, Green, Blue and Alpha and calculate the correct color and opacity
                                color[k] = gradient[prevKey][k] - ((gradient[prevKey][k] - gradient[gradientKey][k]) * gradientPartIndex);
                                if (k < 3) color[k] = Math.round(color[k]);
                            }
                            chartColors[i] = 'rgba(' + color.toString() + ')';
                            break;
                        }
                    }
                }
            } else {
                for (var i = 0, counter = 0; i < setsCount; i++, counter++) {
                    if (counter >= color_set.length) counter = 0; // reset back to the beginning

                    chartColors.push(color_set[counter]);
                }
            }

            var datasets = teleMyChart.config.data.datasets;
            var options = teleMyChart.config.options;

            options.legend.labels.usePointStyle = true;
            if (teleChartFamily == "circle") {
                if (tele_show_data_value) {
                    options.legend.position = 'bottom';
                    options.layout.padding.top = 10;
                    options.layout.padding.bottom = 20;
                    options.layout.padding.left = 20;
                    options.layout.padding.right = 20;
                } else {
                    options.legend.position = 'top';
                }

                options = self.teleHideFunction(options, item, teleChartFamily, chartType);

                options.plugins.datalabels.align = 'center';
                options.plugins.datalabels.anchor = 'end';
                options.plugins.datalabels.borderColor = 'white';
                options.plugins.datalabels.borderRadius = 25;
                options.plugins.datalabels.borderWidth = 2;
                options.plugins.datalabels.clamp = true;
                options.plugins.datalabels.clip = false;

                options.tooltips.callbacks = {
                    title: function(tooltipItem, data) {
                        var tele_self = self;
                        var k_amount = data.datasets[tooltipItem[0].datasetIndex]['data'][tooltipItem[0].index];
                        var tele_selection = chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = chart_data.tele_currency;
                            k_amount = TeleGlobalFunction.tele_monetary(k_amount, tele_currency_id);
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount
                        } else if (tele_selection === 'custom') {
                            var tele_field = chart_data.tele_field;
                            //                                                        tele_type = field_utils.format.char(tele_field);
                            k_amount = field_utils.format.float(k_amount, Float64Array, {digits:[0,item.tele_precision_digits]});
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount + " " + tele_field;
                        } else {
                            k_amount = field_utils.format.float(k_amount, Float64Array, {digits:[0,item.tele_precision_digits]});
                            return data.datasets[tooltipItem[0].datasetIndex]['label'] + " : " + k_amount
                        }
                    },
                    label: function(tooltipItem, data) {
                        return data.labels[tooltipItem.index];
                    },
                }
                for (var i = 0; i < datasets.length; i++) {
                    datasets[i].backgroundColor = chartColors;
                    datasets[i].borderColor = "rgba(255,255,255,1)";
                }
                if (semi_circle && (chartType === "pie" || chartType === "doughnut")) {
                    options.rotation = 1 * Math.PI;
                    options.circumference = 1 * Math.PI;
                }
            } else if (teleChartFamily == "square") {
                options = self.teleHideFunction(options, item, teleChartFamily, chartType);

                options.scales.xAxes[0].gridLines.display = false;
                options.scales.yAxes[0].ticks.beginAtZero = true;

                options.plugins.datalabels.align = 'end';

                options.plugins.datalabels.formatter = function(value, ctx) {
                    var tele_selection = chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = chart_data.tele_currency;
                            var tele_data = value;
                            tele_data = TeleGlobalFunction._onTeleGlobalFormatter(tele_data, item.tele_data_formatting, item.tele_precision_digits);
                            tele_data = TeleGlobalFunction.tele_monetary(tele_data, tele_currency_id);
                           return tele_data;
                        } else if (tele_selection === 'custom') {
                            var tele_field = chart_data.tele_field;
                            return TeleGlobalFunction._onTeleGlobalFormatter(value, item.tele_data_formatting, item.tele_precision_digits) + ' ' + tele_field;

                        } else {
                           return TeleGlobalFunction._onTeleGlobalFormatter(value, item.tele_data_formatting, item.tele_precision_digits);
                        }
                };

                if (chartType === "line") {
                    options.plugins.datalabels.backgroundColor = function(context) {
                        return context.dataset.borderColor;
                    };
                }

                if (chartType === "horizontalBar") {
                    options.scales.xAxes[0].ticks.callback = function(value, index, values) {
                        var tele_selection = chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = chart_data.tele_currency;
                            var tele_data = value;
                            tele_data = TeleGlobalFunction._onTeleGlobalFormatter(tele_data, item.tele_data_formatting, item.tele_precision_digits);
                            tele_data = TeleGlobalFunction.tele_monetary(tele_data, tele_currency_id);
                           return tele_data;
                        } else if (tele_selection === 'custom') {
                            var tele_field = chart_data.tele_field;
                            return TeleGlobalFunction._onTeleGlobalFormatter(value, item.tele_data_formatting, item.tele_precision_digits) + ' ' + tele_field;

                        } else {
                           return TeleGlobalFunction._onTeleGlobalFormatter(value, item.tele_data_formatting, item.tele_precision_digits);
                        }
                    }
                    options.scales.xAxes[0].ticks.beginAtZero = true;
                } else {
                    options.scales.yAxes[0].ticks.callback = function(value, index, values) {
                        var tele_selection = chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = chart_data.tele_currency;
                            var tele_data = value;
                            tele_data = TeleGlobalFunction._onTeleGlobalFormatter(tele_data, item.tele_data_formatting, item.tele_precision_digits);
                            tele_data = TeleGlobalFunction.tele_monetary(tele_data, tele_currency_id);
                           return tele_data;
                        } else if (tele_selection === 'custom') {
                            var tele_field = chart_data.tele_field;
                            return TeleGlobalFunction._onTeleGlobalFormatter(value, item.tele_data_formatting, item.tele_precision_digits) + ' ' + tele_field;

                        } else {
                           return TeleGlobalFunction._onTeleGlobalFormatter(value, item.tele_data_formatting, item.tele_precision_digits);
                        }
                    }
                }

                options.tooltips.callbacks = {
                    label: function(tooltipItem, data) {
                        var tele_self = self;
                        var k_amount = data.datasets[tooltipItem.datasetIndex]['data'][tooltipItem.index];
                        var tele_selection = chart_data.tele_selection;
                        if (tele_selection === 'monetary') {
                            var tele_currency_id = chart_data.tele_currency;
                            k_amount = TeleGlobalFunction.tele_monetary(k_amount, tele_currency_id);
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount
                        } else if (tele_selection === 'custom') {
                            var tele_field = chart_data.tele_field;
                            // tele_type = field_utils.format.char(tele_field);
                            k_amount = field_utils.format.float(k_amount, Float64Array, {digits:[0,item.tele_precision_digits]});
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount + " " + tele_field;
                        } else {
                            k_amount = field_utils.format.float(k_amount, Float64Array,{digits:[0,item.tele_precision_digits]});
                            return data.datasets[tooltipItem.datasetIndex]['label'] + " : " + k_amount
                        }
                    }
                }

                for (var i = 0; i < datasets.length; i++) {
                    switch (teleChartType) {
                        case "bar":
                        case "horizontalBar":
                            if (datasets[i].type && datasets[i].type == "line") {
                                datasets[i].borderColor = chartColors[i];
                                datasets[i].backgroundColor = "rgba(255,255,255,0)";
                                datasets[i]['datalabels'] = {
                                    backgroundColor: chartColors[i],
                                }
                            } else {
                                datasets[i].backgroundColor = chartColors[i];
                                datasets[i].borderColor = "rgba(255,255,255,0)";
                                options.scales.xAxes[0].stacked = stack;
                                options.scales.yAxes[0].stacked = stack;
                            }
                            break;
                        case "line":
                            datasets[i].borderColor = chartColors[i];
                            datasets[i].backgroundColor = "rgba(255,255,255,0)";
                            break;
                        case "area":
                            datasets[i].borderColor = chartColors[i];
                            break;
                    }
                }

            }
            teleMyChart.update();
        },

        onChartCanvasClick: function(evt) {

            var self = this;
//            $(self.$el.find('.tele_pager')).addClass('d-none');
            if (evt.currentTarget.classList.value !== 'tele_list_canvas_click') {
                var item_id = evt.currentTarget.dataset.chartId;
                if (item_id in self.teleUpdateDashboard) {
                    clearInterval(self.teleUpdateDashboard[item_id]);
                    delete self.teleUpdateDashboard[item_id]
                }
                var myChart = self.chart_container[item_id];
                var activePoint = myChart.getElementAtEvent(evt)[0];
                if (activePoint) {
                    var item_data = self.tele_dashboard_data.tele_item_data[item_id];
                    var groupBy = JSON.parse(item_data["tele_chart_data"])['groupby'];
                    if (activePoint._chart.data.domains) {
                        var sequnce = item_data.sequnce ? item_data.sequnce : 0;

                        var domain = activePoint._chart.data.domains[activePoint._index]
                        if (item_data.max_sequnce != 0 && sequnce < item_data.max_sequnce) {
                            self._rpc({
                                model: 'tele_dashboard_ninja.item',
                                method: 'tele_fetch_drill_down_data',
                                args: [item_id, domain, sequnce]
                            }).then(function(result) {
                                self.tele_dashboard_data.tele_item_data[item_id]['sequnce'] = result.sequence;
                                self.tele_dashboard_data.tele_item_data[item_id]['isDrill'] = true;
                                if (result.tele_chart_data) {
                                    self.tele_dashboard_data.tele_item_data[item_id]['tele_dashboard_item_type'] = result.tele_chart_type;
                                    self.tele_dashboard_data.tele_item_data[item_id]['tele_chart_data'] = result.tele_chart_data;
                                    if (self.tele_dashboard_data.tele_item_data[item_id].domains) {
                                        self.tele_dashboard_data.tele_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.tele_chart_data).previous_domain;
                                    } else {
                                        self.tele_dashboard_data.tele_item_data[item_id]['domains'] = {}
                                        self.tele_dashboard_data.tele_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.tele_chart_data).previous_domain;
                                    }
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_drill_up").removeClass('d-none');
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_chart_info").removeClass('d-none')
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_color_option").removeClass('d-none')
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_quick_edit_action_popup").removeClass('d-sm-block ');
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_more_action").addClass('d-none');

                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".card-body").empty();
                                    var item_data = self.tele_dashboard_data.tele_item_data[item_id]
                                    self._renderChart($(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]), item_data);
                                } else {
                                    if ('domains' in self.tele_dashboard_data.tele_item_data[item_id]) {
                                        self.tele_dashboard_data.tele_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.tele_list_view_data).previous_domain;
                                    } else {
                                        self.tele_dashboard_data.tele_item_data[item_id]['domains'] = {}
                                        self.tele_dashboard_data.tele_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.tele_list_view_data).previous_domain;
                                    }
                                    self.tele_dashboard_data.tele_item_data[item_id]['isDrill'] = true;
                                    self.tele_dashboard_data.tele_item_data[item_id]['sequnce'] = result.sequence;
                                    self.tele_dashboard_data.tele_item_data[item_id]['tele_list_view_data'] = result.tele_list_view_data;
                                    self.tele_dashboard_data.tele_item_data[item_id]['tele_list_view_type'] = result.tele_list_view_type;
                                    self.tele_dashboard_data.tele_item_data[item_id]['tele_dashboard_item_type'] = 'tele_list_view';

                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_drill_up").removeClass('d-none');

                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_chart_info").addClass('d-none')
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_color_option").addClass('d-none')
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".card-body").empty();
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_quick_edit_action_popup").removeClass('d-sm-block ');

                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_more_action").addClass('d-none');
                                    var item_data = self.tele_dashboard_data.tele_item_data[item_id]
                                    var $container = self.renderListViewData(item_data);
                                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".card-body").append($container).addClass('tele_overflow');
                                }
                            });
                        } else {
                        if (item_data.action) {
                                if (!item_data.tele_is_client_action){
                                    var action = Object.assign({}, item_data.action);
                                    if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree', 'list');
                                    for (var i = 0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1];
                                    action['domain'] = domain || [];
                                    action['search_view_id'] = [action.search_view_id, 'search']
                                }else{
                                    var action = Object.assign({}, item_data.action[0]);
                                    if (action.params){
                                        action.params.default_active_id || 'mailbox_inbox';
                                        }else{
                                            action.params = {
                                            'default_active_id': 'mailbox_inbox'
                                            };
                                            action.context = {}
                                            action.context.params = {
                                            'active_model': false
                                            };
                                        }
                                }
                            } else {
                                var action = {
                                    name: _t(item_data.name),
                                    type: 'ir.actions.act_window',
                                    res_model: item_data.tele_model_name,
                                    domain: domain || [],
                                    context: {
                                        'group_by': groupBy ? groupBy:false ,
                                    },
                                    views: [
                                        [false, 'list'],
                                        [false, 'form']
                                    ],
                                    view_mode: 'list',
                                    target: 'current',
                                }
                            }
                            if (item_data.tele_show_records) {

                                self.do_action(action, {
                                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                                });
                            }
                        }
                    }
                }
            } else {
                var item_id = $(evt.target).parent().data().itemId;
                if (this.teleUpdateDashboard[item_id]) {
                    clearInterval(this.teleUpdateDashboard[item_id]);
                    delete self.teleUpdateDashboard[item_id];
                }
                var item_data = self.tele_dashboard_data.tele_item_data[item_id]
                if (self.tele_dashboard_data.tele_item_data[item_id].max_sequnce) {

                    var sequence = item_data.sequnce ? item_data.sequnce : 0

                    var domain = $(evt.target).parent().data().domain;

                    if ($(evt.target).parent().data().last_seq !== sequence) {
                        self._rpc({
                            model: 'tele_dashboard_ninja.item',
                            method: 'tele_fetch_drill_down_data',
                            args: [item_id, domain, sequence]
                        }).then(function(result) {
                            if (result.tele_list_view_data) {
                                if (self.tele_dashboard_data.tele_item_data[item_id].domains) {
                                    self.tele_dashboard_data.tele_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.tele_list_view_data).previous_domain;
                                } else {
                                    self.tele_dashboard_data.tele_item_data[item_id]['domains'] = {}
                                    self.tele_dashboard_data.tele_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.tele_list_view_data).previous_domain;
                                }
                                self.tele_dashboard_data.tele_item_data[item_id]['isDrill'] = true;
                                self.tele_dashboard_data.tele_item_data[item_id]['sequnce'] = result.sequence;
                                self.tele_dashboard_data.tele_item_data[item_id]['tele_list_view_data'] = result.tele_list_view_data;
                                self.tele_dashboard_data.tele_item_data[item_id]['tele_list_view_type'] = result.tele_list_view_type;
                                self.tele_dashboard_data.tele_item_data[item_id]['tele_dashboard_item_type'] = 'tele_list_view';
                                self.tele_dashboard_data.tele_item_data[item_id]['sequnce'] = result.sequence;
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".card-body").empty();
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_search_plus").addClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_search_minus").addClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_drill_up").removeClass('d-none');
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_pager").addClass('d-none');
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_action_export").addClass('d-none');
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_quick_edit_action_popup").removeClass('d-sm-block ');

                                var item_data = self.tele_dashboard_data.tele_item_data[item_id]
                                var $container = self.renderListViewData(item_data);
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".card-body").append($container);
                            } else {
                                self.tele_dashboard_data.tele_item_data[item_id]['tele_chart_data'] = result.tele_chart_data;
                                self.tele_dashboard_data.tele_item_data[item_id]['sequnce'] = result.sequence;
                                self.tele_dashboard_data.tele_item_data[item_id]['tele_dashboard_item_type'] = result.tele_chart_type;
                                self.tele_dashboard_data.tele_item_data[item_id]['isDrill'] = true;
                                if (self.tele_dashboard_data.tele_item_data[item_id].domains) {
                                    self.tele_dashboard_data.tele_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.tele_chart_data).previous_domain;
                                } else {
                                    self.tele_dashboard_data.tele_item_data[item_id]['domains'] = {}
                                    self.tele_dashboard_data.tele_item_data[item_id]['domains'][result.sequence] = JSON.parse(result.tele_chart_data).previous_domain;
                                }
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_chart_info").removeClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_color_option").removeClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_search_plus").addClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_search_minus").addClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_drill_up").removeClass('d-none');
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_pager").addClass('d-none');
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_quick_edit_action_popup").removeClass('d-sm-block ');
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_action_export").addClass('d-none');
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".card-body").empty();
                                var item_data = self.tele_dashboard_data.tele_item_data[item_id]
                                self._renderChart($(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]), item_data);
                            }
                        });
                    }
                }
            }
            evt.stopPropagation();
        },

        teleOnDrillUp: function(e) {
            var self = this;
            var item_id = e.currentTarget.dataset.itemId;
            var item_data = self.tele_dashboard_data.tele_item_data[item_id];
            var domain;
            if(item_data) {

                if ('domains' in item_data) {
                    domain = item_data['domains'][item_data.sequnce - 1] ? item_data['domains'][item_data.sequnce - 1] : []
                    var sequnce = item_data.sequnce - 2;
                    if (sequnce >= 0) {
                        self._rpc({
                            model: 'tele_dashboard_ninja.item',
                            method: 'tele_fetch_drill_down_data',
                            args: [item_id, domain, sequnce]
                        }).then(function(result) {
                            self.tele_dashboard_data.tele_item_data[item_id]['tele_chart_data'] = result.tele_chart_data;
                            self.tele_dashboard_data.tele_item_data[item_id]['sequnce'] = result.sequence;
                            if (result.tele_chart_type)  self.tele_dashboard_data.tele_item_data[item_id]['tele_dashboard_item_type'] = result.tele_chart_type;
                            $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_drill_up").removeClass('d-none');
                            $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".card-body").empty();
                            if (result.tele_chart_data) {
                                var item_data = self.tele_dashboard_data.tele_item_data[item_id];
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_chart_info").removeClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_color_option").removeClass('d-none')
                                self._renderChart($(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]), item_data);

                            } else {
                                self.tele_dashboard_data.tele_item_data[item_id]['tele_list_view_data'] = result.tele_list_view_data;
                                self.tele_dashboard_data.tele_item_data[item_id]['tele_list_view_type'] = result.tele_list_view_type;
                                self.tele_dashboard_data.tele_item_data[item_id]['tele_dashboard_item_type'] = 'tele_list_view';
                                var item_data = self.tele_dashboard_data.tele_item_data[item_id]
                                var $container = self.renderListViewData(item_data);
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_pager").addClass('d-none');
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_chart_info").addClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_color_option").addClass('d-none')
                                $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".card-body").append($container);
                            }

                        });

                    } else {
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_drill_up").addClass('d-none');
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_chart_info").removeClass('d-none')
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_color_option").removeClass('d-none')
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_quick_edit_action_popup").addClass('d-sm-block ');
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_more_action").removeClass('d-none');
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_action_export").removeClass('d-none')
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_search_plus").removeClass('d-none')
                        $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_search_minus").removeClass('d-none')
                        self.teleFetchChartItem(item_id)
//                        $(self.$el.find('.tele_pager')).removeClass('d-none');
                        var updateValue = self.tele_dashboard_data.tele_set_interval;
                        if (updateValue) {
                            var updateinterval = setInterval(function() {
                                self.teleFetchChartItem(item_id)
                            }, updateValue);
                            self.teleUpdateDashboard[item_id] = updateinterval;
                        }
                    }

                } else {
                    if(!domain){
                    $(self.$el.find(".grid-stack-item[gs-id=" + item_id + "]").children()[0]).find(".tele_dashboard_item_drill_up").addClass('d-none');
                }

                }
            }

            e.stopPropagation();
        },

        teleFetchChartItem: function(id) {
            var self = this;
            var item_data = self.tele_dashboard_data.tele_item_data[id];

            return self._rpc({
                model: 'tele_dashboard_ninja.board',
                method: 'tele_fetch_item',
                args: [
                    [item_data.id], self.tele_dashboard_id, self.teleGetParamsForItemFetch(id)
                ],
                context: self.getContext(),
            }).then(function(new_item_data) {
                this.tele_dashboard_data.tele_item_data[id] = new_item_data[id];
                $(self.$el.find(".grid-stack-item[gs-id=" + id + "]").children()[0]).find(".card-body").empty();
                var item_data = self.tele_dashboard_data.tele_item_data[id]
                if (item_data.tele_list_view_data) {
                    var item_view = $(self.$el.find(".grid-stack-item[gs-id=" + id + "]").children()[0]);
                    var $container = self.renderListViewData(item_data);
                    item_view.find(".card-body").append($container);
                    var tele_length = JSON.parse(item_data['tele_list_view_data']).data_rows.length
                    if (new_item_data["tele_list_view_type"] === "ungrouped" && JSON.parse(item_data['tele_list_view_data']).data_rows.length) {
                        item_view.find('.tele_pager').removeClass('d-none');
                        if (item.tele_record_count <= item.tele_pagination_limit) item_view.find('.tele_load_next').addClass('tele_event_offer_list');
                        item_view.find('.tele_value').text("1-" + JSON.parse(item_data['tele_list_view_data']).data_rows.length);
                    } else {
                        item_view.find('.tele_pager').addClass('d-none');
                    }
                } else {
                    self._renderChart($(self.$el.find(".grid-stack-item[gs-id=" + id + "]").children()[0]), item_data);
                }
            }.bind(this));
        },

        onChartMoreInfoClick: function(evt) {
            var self = this;
            var item_id = evt.currentTarget.dataset.itemId;
            var item_data = self.tele_dashboard_data.tele_item_data[item_id];
            var groupBy = item_data.tele_chart_groupby_type === 'relational_type' ? item_data.tele_chart_relation_groupby_name : item_data.tele_chart_relation_groupby_name + ':' + item_data.tele_chart_date_groupby;
            var domain = JSON.parse(item_data.tele_chart_data).previous_domain

            if (item_data.tele_show_records) {
                if (item_data.action) {

                    if (!item_data.tele_is_client_action){
                        var action = Object.assign({}, item_data.action);
                        if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree', 'list');
                            for (var i = 0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1];
                                action['domain'] = item_data.tele_domain || [];
                                action['search_view_id'] = [action.search_view_id, 'search']
                        }else{
                            var action = Object.assign({}, item_data.action[0]);
                            if (action.params){
                                action.params.default_active_id || 'mailbox_inbox';
                                }else{
                                    action.params = {
                                    'default_active_id': 'mailbox_inbox'
                                    }
                                    action.context = {}
                                    action.context.params = {
                                    'active_model': false
                                    };
                                }
                            }
                } else {
                    var action = {
                        name: _t(item_data.name),
                        type: 'ir.actions.act_window',
                        res_model: item_data.tele_model_name,
                        domain: domain || [],
                        context: {
                            'group_by': groupBy ? groupBy:false ,
                        },
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        view_mode: 'list',
                        target: 'current',
                    }
                }
                self.do_action(action, {
                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                });
            }
        },

        _teleRenderNoItemView: function() {
            $('.tele_dashboard_items_list').remove();
            var self = this;
            $(QWeb.render('teleNoItemView')).appendTo(self.$el)

        },

        _teleRenderEditMode: function() {

            var self = this;
            self.tele_mode = 'edit';
            self.tele_remove_update_interval();

            $('#tele_dashboard_title_input').val(self.tele_dashboard_data.name);

            $('.tele_am_element').addClass("tele_hide");
            $('.tele_em_element').removeClass("tele_hide");
            $('.tele_dashboard_print_pdf').addClass("tele_hide");

            self.$el.find('.tele_item_click').addClass('tele_item_not_click').removeClass('tele_item_click');
            self.$el.find('.tele_dashboard_item').removeClass('tele_dashboard_item_header_hover');
            self.$el.find('.tele_dashboard_item_header').removeClass('tele_dashboard_item_header_hover');

            self.$el.find('.tele_dashboard_item_l2').removeClass('tele_dashboard_item_header_hover');
            self.$el.find('.tele_dashboard_item_header_l2').removeClass('tele_dashboard_item_header_hover');

            self.$el.find('.tele_dashboard_item_l5').removeClass('tele_dashboard_item_header_hover');

            self.$el.find('.tele_dashboard_item_button_container').removeClass('tele_dashboard_item_header_hover');

            self.$el.find('.tele_dashboard_link').addClass("tele_hide")
            self.$el.find('.tele_dashboard_top_settings').addClass("tele_hide")
            self.$el.find('.tele_dashboard_edit_mode_settings').removeClass("tele_hide")

            // Adding Chart grab able cals
            self.$el.find('.tele_start_tv_dashboard').addClass('tele_hide');
            self.$el.find('.tele_chart_container').addClass('tele_item_not_click');
            self.$el.find('.tele_list_view_container').addClass('tele_item_not_click');

            if (self.grid) {
                self.grid.enable();
            }
        },


        _teleRenderActiveMode: function() {
            var self = this
            self.tele_mode = 'active';

            if (self.grid && $('.grid-stack').data('gridstack')) {
                $('.grid-stack').data('gridstack').disable();
            }

            if (self.tele_dashboard_data.tele_child_boards) {
//                var dash_name = $('ul[id="tele_dashboard_layout_dropdown_container"] li[class="tele_dashboard_layout_event tele_layout_selected"] span').text()
                var $layout_container = $(QWeb.render('tele_dn_layout_container', {
                    tele_selected_board_id: self.tele_dashboard_data.tele_selected_board_id,
                    tele_child_boards: self.tele_dashboard_data.tele_child_boards,
                    tele_multi_layout: self.tele_dashboard_data.multi_layouts,
                    tele_dash_name: self.tele_dashboard_data.name
                }));
                $('#tele_dashboard_title .tele_am_element').replaceWith($layout_container);
                $('#tele_dashboard_title_label').replaceWith($layout_container);
            } else {
                $('#tele_dashboard_title_label').text(self.tele_dashboard_data.name);
            }

            $('#tele_dashboard_title_label').text(self.tele_dashboard_data.name);

            $('.tele_am_element').removeClass("tele_hide");
            $('.tele_em_element').addClass("tele_hide");
            $('.tele_dashboard_print_pdf').removeClass("tele_hide");
            if (self.tele_dashboard_data.tele_item_data) $('.tele_am_content_element').removeClass("tele_hide");

            self.$el.find('.tele_item_not_click').addClass('tele_item_click').removeClass('tele_item_not_click')
            self.$el.find('.tele_dashboard_item').addClass('tele_dashboard_item_header_hover')
            self.$el.find('.tele_dashboard_item_header').addClass('tele_dashboard_item_header_hover')

            self.$el.find('.tele_dashboard_item_l2').addClass('tele_dashboard_item_header_hover')
            self.$el.find('.tele_dashboard_item_header_l2').addClass('tele_dashboard_item_header_hover')

            //      For layout 5
            self.$el.find('.tele_dashboard_item_l5').addClass('tele_dashboard_item_header_hover')


            self.$el.find('.tele_dashboard_item_button_container').addClass('tele_dashboard_item_header_hover');

            self.$el.find('.tele_dashboard_top_settings').removeClass("tele_hide")
            self.$el.find('.tele_dashboard_edit_mode_settings').addClass("tele_hide")

            self.$el.find('.tele_start_tv_dashboard').removeClass('tele_hide');
            self.$el.find('.tele_chart_container').removeClass('tele_item_not_click tele_item_click');
            self.$el.find('.tele_list_view_container').removeClass('tele_item_click');

            self.tele_set_update_interval();
            self.grid.commit();
        },

        _teleToggleEditMode: function() {
            var self = this
            if (self.teleDashboardEditMode) {
                self._teleRenderActiveMode()
                self.teleDashboardEditMode = false
            } else if (!self.teleDashboardEditMode) {
                self._teleRenderEditMode()
                self.teleDashboardEditMode = true
            }

        },

        onAddItemTypeClick: function(e) {
            var self = this;
            if (e.currentTarget.dataset.item !== "tele_json") {
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'tele_dashboard_ninja.item',
                    view_id: 'tele_dashboard_ninja_list_form_view',
                    views: [
                        [false, 'form']
                    ],
                    target: 'current',
                    context: {
                        'tele_dashboard_id': self.tele_dashboard_id,
                        'tele_dashboard_item_type': e.currentTarget.dataset.item,
                        'form_view_ref': 'tele_dashboard_ninja.item_form_view',
                        'form_view_initial_mode': 'edit',
                        'tele_set_interval': self.tele_dashboard_data.tele_set_interval,
                        'tele_data_formatting':self.tele_dashboard_data.tele_data_formatting,
                    },
                }, {
                    on_reverse_breadcrumb: this.on_reverse_breadcrumb,
                });
            } else {
                self.teleImportItemJson(e);
            }
        },

        teleImportItemJson: function(e) {
            var self = this;
            $('.tele_input_import_item_button').click();
        },

        teleImportItem: function(e) {
            var self = this;
            var fileReader = new FileReader();
            fileReader.onload = function() {
                $('.tele_input_import_item_button').val('');
//                framework.blockUI();
                self._rpc({
                    model: 'tele_dashboard_ninja.board',
                    method: 'tele_import_item',
                    args: [self.tele_dashboard_id],
                    kwargs: {
                        file: fileReader.result,
                        dashboard_id: self.tele_dashboard_id
                    }
                }).then(function(result) {
                    if (result === "Success") {

                        $.when(self.tele_fetch_data()).then(function() {
                            $.when(self.tele_fetch_items_data()).then(function(result){
                                self.teleRenderDashboard();
                            });

//                            framework.unblockUI();
                        });
                    }
                });
            };
            fileReader.readAsText($('.tele_input_import_item_button').prop('files')[0]);
        },

        _onTeleAddLayoutClick: function() {
            var self = this;

            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'tele_dashboard_ninja.item',
                view_id: 'tele_dashboard_ninja_list_form_view',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                context: {
                    'tele_dashboard_id': self.tele_dashboard_id,
                    'form_view_ref': 'tele_dashboard_ninja.item_form_view',
                    'form_view_initial_mode': 'edit',
                },
            }, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });
        },

        _onTeleEditLayoutClick: function() {
            var self = this;
            self.grid.setStatic(false);
            self._teleRenderEditMode();
        },

        _onTeleSaveLayoutClick: function() {
            this.grid.setStatic(true)
            var self = this;
            //        Have  to save dashboard here
            var dashboard_title = $('#tele_dashboard_title_input').val();
            if (dashboard_title != false && dashboard_title != 0 && dashboard_title !== self.tele_dashboard_data.name) {
                self.tele_dashboard_data.name = dashboard_title;
                var model = 'tele_dashboard_ninja.board';
                var rec_id = self.tele_dashboard_id;

                if(this.tele_dashboard_data.tele_selected_board_id && this.tele_dashboard_data.tele_child_boards){
                    this.tele_dashboard_data.tele_child_boards[this.tele_dashboard_data.tele_selected_board_id][0] = dashboard_title;
                    if (this.tele_dashboard_data.tele_selected_board_id !== 'tele_default'){
                        model = 'tele_dashboard_ninja.child_board';
                        rec_id = this.tele_dashboard_data.tele_selected_board_id;
                    }
                }
                this._rpc({
                    model: model,
                    method: 'write',
                    args: [rec_id, {
                        'name': dashboard_title
                    }],
                })
            }
            if (this.tele_dashboard_data.tele_item_data) self._teleSaveCurrentLayout();
            self._teleRenderActiveMode();
        },

        _onTeleCreateLayoutClick: function() {
            var self = this;
            self.grid.setStatic(true)
            var dashboard_title = $('#tele_dashboard_title_input').val();
            if (dashboard_title ==="") {
                self.call('notification', 'notify', {
                    message: "Dashboard Name is required to save as New Layout.",
                    type: 'warning',
                });
            } else{
                if (!self.tele_dashboard_data.tele_child_boards){
                    self.tele_dashboard_data.tele_child_boards = {
                        'tele_default': [this.tele_dashboard_data.name, self.tele_dashboard_data.tele_gridstack_config]
                    }
                }
                this.tele_dashboard_data.name = dashboard_title;

                var grid_config = self.tele_get_current_gridstack_config();
                this._rpc({
                    model: 'tele_dashboard_ninja.board',
                    method: 'update_child_board',
                    args: ['create', self.tele_dashboard_id, {
                        "tele_gridstack_config": JSON.stringify(grid_config),
                        "tele_dashboard_ninja_id": self.tele_dashboard_id,
                        "name": dashboard_title,
                        "tele_active": true,
                        "company_id": self.tele_dashboard_data.tele_company_id,
                    }],
                }).then(function(res_id){
                    self.tele_update_child_board_value(dashboard_title, res_id, grid_config),
                    self._teleRenderActiveMode();
                });
            }
        },

        tele_update_child_board_value: function(dashboard_title, res_id, grid_config){
            var self = this;
            var child_board_id = res_id.toString();
            self.tele_dashboard_data.tele_selected_board_id = child_board_id;
            var update_data = {};
            update_data[child_board_id] = [dashboard_title, JSON.stringify(grid_config)];
            self.tele_dashboard_data.tele_child_boards = _.extend(update_data,self.tele_dashboard_data.tele_child_boards);
        },

        _onTeleCancelLayoutClick: function() {
            var self = this;
            //        render page again
            $.when(self.tele_fetch_data()).then(function() {
                $.when(self.tele_fetch_items_data()).then(function(result){
                    self.teleRenderDashboard();
                    self.tele_set_update_interval();
                });
            });
        },

        _onTeleItemClick: function(e) {
            var self = this;
            //  To Handle only allow item to open when not clicking on item
            if (self.teleAllowItemClick) {



                e.preventDefault();
                if (e.target.title != "Customize Item") {
                    var item_id = parseInt(e.currentTarget.firstElementChild.id);
                    var item_data = self.tele_dashboard_data.tele_item_data[item_id];
                    if (item_data && item_data.tele_show_records) {

                        if (item_data.action) {
                            if (!item_data.tele_is_client_action){
                                var action = Object.assign({}, item_data.action);
                                if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree', 'list');
                                for (var i = 0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1];
                                action['domain'] = item_data.tele_domain || [];
                                action['search_view_id'] = [action.search_view_id, 'search']
                            }else{
                                var action = Object.assign({}, item_data.action[0]);
                                if (action.params){
                                    action.params.default_active_id || 'mailbox_inbox';
                                    }else{
                                        action.params = {
                                        'default_active_id': 'mailbox_inbox'
                                        }
                                        action.context = {}
                                        action.context.params = {
                                        'active_model': false
                                        };
                                    }
                            }

                        } else {
                            var action = {
                                name: _t(item_data.name),
                                type: 'ir.actions.act_window',
                                res_model: item_data.tele_model_name,
                                domain: item_data.tele_domain || "[]",
                                views: [
                                    [false, 'list'],
                                    [false, 'form']
                                ],
                                view_mode: 'list',
                                target: 'current',
                            }
                        }
                        self.do_action(action, {
                            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                        });
                    }
                }
            } else {
                self.teleAllowItemClick = true;
            }
        },

        _onTeleItemCustomizeClick: function(e) {
            var self = this;
            var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('gs-id'));
            self.tele_open_item_form_page(id);

            e.stopPropagation();
        },

        tele_open_item_form_page: function(id) {
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'tele_dashboard_ninja.item',
                view_id: 'tele_dashboard_ninja_list_form_view',
                views: [
                    [false, 'form']
                ],
                target: 'current',
                context: {
                    'form_view_ref': 'tele_dashboard_ninja.item_form_view',
                    'form_view_initial_mode': 'edit',
                },
                res_id: id
            }, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });
        },


        // Note : this is exceptionally bind to this function.
        teleUpdateDashboardItem: function(ids) {
            var self = this;
            for (var i = 0; i < ids.length; i++) {

                var item_data = self.tele_dashboard_data.tele_item_data[ids[i]]
                if (item_data['tele_dashboard_item_type'] == 'tele_list_view') {
                    var item_view = self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]");
                    var name = item_data.name ?item_data.name : item_data.tele_model_display_name;
                    item_view.children().find('.tele_list_view_heading').prop('title', name);
                    item_view.children().find('.tele_list_view_heading').text(name);
                    item_view.find('.card-body').empty();
                    item_view.find('.tele_dashboard_item_drill_up').addClass('d-none')
                    item_view.find('.tele_dashboard_item_action_export').removeClass('d-none')
                    item_view.find('.tele_dashboard_quick_edit_action_popup ').removeClass('d-none')
                    item_view.find('.card-body').append(self.renderListViewData(item_data));
                    var rows = JSON.parse(item_data['tele_list_view_data']).data_rows;
                    var tele_length = rows ? rows.length : false;
                    if (tele_length) {
                        if (item_view.find('.tele_pager_name')) {
                            item_view.find('.tele_pager_name').empty();
                            var $tele_pager_container = QWeb.render('tele_pager_template', {
                                item_id: ids[i],
                                intial_count: item_data.tele_pagination_limit,
                                offset : 1
                            })
                            item_view.find('.tele_pager_name').append($($tele_pager_container));
                        }

                            if (tele_length < item_data.tele_pagination_limit) item_view.find('.tele_load_next').addClass('tele_event_offer_list');
                                item_view.find('.tele_value').text("1-" + JSON.parse(item_data['tele_list_view_data']).data_rows.length);

                            if (item_data.tele_record_data_limit == item_data.tele_pagination_limit || item_data.tele_record_count==item_data.tele_pagination_limit) {
                                item_view.find('.tele_load_next').addClass('tele_event_offer_list');
                            }
                    } else {
                        item_view.find('.tele_pager').addClass('d-none');
                    }
                } else if (item_data['tele_dashboard_item_type'] == 'tele_tile') {
                    var item_view = self._teleRenderDashboardTile(item_data);
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find(".tele_dashboard_item_hover").replaceWith($(item_view).find('.tele_dashboarditem_id'));
                } else if (item_data['tele_dashboard_item_type'] == 'tele_kpi') {
                    var item_view = self.renderKpi(item_data);
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find(".tele_dashboard_item_hover").replaceWith($(item_view).find('.tele_dashboarditem_id'));
                } else  if (item_data['tele_dashboard_item_type'] == 'tele_to_do'){
//                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").empty();
//                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").append(self.teleRenderToDoDashboardView(item_data));
                }else{
                    self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]").find(".card-body").empty()
                    self._renderChart(self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]"), item_data);
                }

            }
            self.grid.setStatic(true);
        },

        _onTeleDeleteItemClick: function(e) {
            var self = this;
            var item = $($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0])
            var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('gs-id'));
            self.tele_delete_item(id, item);
            e.stopPropagation();
        },

        tele_delete_item: function(id, item) {
            var self = this;
            Dialog.confirm(this, (_t("Are you sure you want to remove this item?")), {
                confirm_callback: function() {

                    self._rpc({
                        model: 'tele_dashboard_ninja.item',
                        method: 'unlink',
                        args: [id],
                    }).then(function(result) {

                        // Clean Item Remove Process.
                        self.tele_remove_update_interval();
                        delete self.tele_dashboard_data.tele_item_data[id];
                        self.grid.removeWidget(item);
                        self.tele_set_update_interval();

                        if (Object.keys(self.tele_dashboard_data.tele_item_data).length > 0) {
                            self._teleSaveCurrentLayout();
                        }
                        else {
                            self._teleRenderNoItemView();
                            self.teleRenderDashboard();
                        }
                        $.when(self.tele_fetch_data()).then(function() {
                            $.when(self.tele_fetch_items_data()).then(function(){
                                self.tele_remove_update_interval();
                                self.teleRenderDashboard();
                                self.tele_set_update_interval();
                            });
                        });
                    });
                },
            });
        },
       tele_add_dashboard_item_on_empty: function(e){
       var self = this;
            if (e.currentTarget.dataset.item !== "tele_json") {
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'tele_dashboard_ninja.item',
                    view_id: 'tele_dashboard_ninja_list_form_view',
                    views: [
                        [false, 'form']
                    ],
                    target: 'current',
                    context: {
                        'tele_dashboard_id': self.tele_dashboard_id,
                        'form_view_ref': 'tele_dashboard_ninja.item_form_view',
                        'form_view_initial_mode': 'edit',
                    },
                }, {
                    on_reverse_breadcrumb: this.on_reverse_breadcrumb,
                });
            } else {
                self.teleImportItemJson(e);
            }
       },

        _teleSaveCurrentLayout: function() {
            var self = this;
            var grid_config = self.tele_get_current_gridstack_config();
            var model = 'tele_dashboard_ninja.child_board';
            var rec_id = self.tele_dashboard_data.tele_gridstack_config_id;
            self.tele_dashboard_data.tele_gridstack_config = JSON.stringify(grid_config);
            if(this.tele_dashboard_data.tele_selected_board_id && this.tele_dashboard_data.tele_child_boards){
                this.tele_dashboard_data.tele_child_boards[this.tele_dashboard_data.tele_selected_board_id][1] = JSON.stringify(grid_config);
                if (this.tele_dashboard_data.tele_selected_board_id !== 'tele_default'){
                    rec_id = this.tele_dashboard_data.tele_selected_board_id;
                }
            }
            if (!config.device.isMobile) {
                this._rpc({
                model: model,
                method: 'write',
                args: [rec_id, {
                    "tele_gridstack_config": JSON.stringify(grid_config)
                }],
            });
            }
        },

        tele_get_current_gridstack_config: function(){
            var self = this;
            if (document.querySelector('.grid-stack') && document.querySelector('.grid-stack').gridstack){
                var items = document.querySelector('.grid-stack').gridstack.el.gridstack.engine.nodes;
            }
            var grid_config = {}

//            if (self.tele_dashboard_data.tele_gridstack_config && config.device.isMobile) {
//                _.extend(grid_config, JSON.parse(self.tele_dashboard_data.tele_gridstack_config))
//            }
            if (items){
                for (var i = 0; i < items.length; i++) {
                    grid_config[items[i].id] = {
                        'x': items[i].x,
                        'y': items[i].y,
                        'w': items[i].w,
                        'h': items[i].h,
                    }
                }
            }
            return grid_config;
        },

        _renderListView: function(item, grid) {
            var self = this;
            var list_view_data = JSON.parse(item.tele_list_view_data),
                pager = true,
                item_id = item.id,
                data_rows = list_view_data.data_rows,
                length = data_rows ? data_rows.length: false,
                item_title = item.name;
            var $teleItemContainer = self.renderListViewData(item);
            var  tele_data_calculation_type = self.tele_dashboard_data.tele_item_data[item_id].tele_data_calculation_type
            var $tele_gridstack_container = $(QWeb.render('tele_gridstack_list_view_container', {
                tele_chart_title: item_title,
                teleIsDashboardManager: self.tele_dashboard_data.tele_dashboard_manager,
                teleIsUser: true,
                tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                item_id: item_id,
                count: '1-' + length,
                offset: 1,
                intial_count: length,
                tele_pager: pager,
                calculation_type: tele_data_calculation_type
            })).addClass('tele_dashboarditem_id');

            if (item.tele_pagination_limit < length  ) {
                $tele_gridstack_container.find('.tele_load_next').addClass('tele_event_offer_list');
            }
            if (length < item.tele_pagination_limit ) {
                $tele_gridstack_container.find('.tele_load_next').addClass('tele_event_offer_list');
            }
            if (item.tele_record_data_limit === item.tele_pagination_limit){
                   $tele_gridstack_container.find('.tele_load_next').addClass('tele_event_offer_list');
            }
            if (length == 0){
                $tele_gridstack_container.find('.tele_pager').addClass('d-none');
            }
            if (item.tele_pagination_limit==0){
            $tele_gridstack_container.find('.tele_pager_name').addClass('d-none');
            }

            $tele_gridstack_container.find('.card-body').append($teleItemContainer);
            if (item.tele_data_calculation_type === 'query' || item.tele_list_view_type === "ungrouped"){
                $tele_gridstack_container.find('.tele_list_canvas_click').removeClass('tele_list_canvas_click');
            }
            item.$el = $tele_gridstack_container;
            if (item_id in self.gridstackConfig) {
                if (config.device.isMobile){
                    grid.addWidget($tele_gridstack_container[0], {x:self.gridstackConfig[item_id].x, y:self.gridstackConfig[item_id].y, w:self.gridstackConfig[item_id].w, h:self.gridstackConfig[item_id].h, autoPosition:true, minW:3, maxW:null, minH:3, maxH:null, id:item_id});
                }
                else{
                    grid.addWidget($tele_gridstack_container[0], {x:self.gridstackConfig[item_id].x, y:self.gridstackConfig[item_id].y, w:self.gridstackConfig[item_id].w, h:self.gridstackConfig[item_id].h, autoPosition:false, minW:3, maxW:null, minH:3, maxH:null, id:item_id});
                }
            } else {
                grid.addWidget($tele_gridstack_container[0], {x:0, y:0, w:5, h:4, autoPosition:true, minW:4, maxW:null, minH:3, maxH:null, id:item_id});
            }
        },

        renderListViewData: function(item) {
            var self = this;
            var list_view_data = JSON.parse(item.tele_list_view_data);
            var item_id = item.id,
                data_rows = list_view_data.data_rows,
                item_title = item.name;
            if (item.tele_list_view_type === "ungrouped" && list_view_data) {
                if (list_view_data.date_index) {
                    var index_data = list_view_data.date_index;
                    for (var i = 0; i < index_data.length; i++) {
                        for (var j = 0; j < list_view_data.data_rows.length; j++) {
                            var index = index_data[i]
                            var date = list_view_data.data_rows[j]["data"][index]
                            if (date) {
                                if (list_view_data.fields_type[index] === 'date'){
                                    list_view_data.data_rows[j]["data"][index] = moment(new Date(date)).format(this.date_format) , {}, {timezone: false};
                                }else{
                                    list_view_data.data_rows[j]["data"][index] = moment(new Date(date+" UTC")).format(this.datetime_format), {}, {timezone: false};
                                }
                            }else{
                                list_view_data.data_rows[j]["data"][index] = "";
                            }
                        }
                    }
                }
            }
            if (list_view_data) {
                for (var i = 0; i < list_view_data.data_rows.length; i++) {
                    for (var j = 0; j < list_view_data.data_rows[0]["data"].length; j++) {
                        if (typeof(list_view_data.data_rows[i].data[j]) === "number" || list_view_data.data_rows[i].data[j]) {
                            if (typeof(list_view_data.data_rows[i].data[j]) === "number") {
                                list_view_data.data_rows[i].data[j] = field_utils.format.float(list_view_data.data_rows[i].data[j], Float64Array, {digits:[0,item.tele_precision_digits]})
                            }
                        } else {
                            list_view_data.data_rows[i].data[j] = "";
                        }
                    }
                }
            }
            var $teleItemContainer = $(QWeb.render('tele_list_view_table', {
                list_view_data: list_view_data,
                item_id: item_id,
                list_type: item.tele_list_view_type,
                isDrill: self.tele_dashboard_data.tele_item_data[item_id]['isDrill']
            }));
            self.list_container = $teleItemContainer;
            if (list_view_data){
                var $teleitemBody = self.teleListViewBody(list_view_data,item_id)
                self.list_container.find('.tele_table_body').append($teleitemBody)
            }
            if (item.tele_list_view_type === "ungrouped") {
                $teleItemContainer.find('.tele_list_canvas_click').removeClass('tele_list_canvas_click');
            }

            if (!item.tele_show_records) {
                $teleItemContainer.find('#tele_item_info').hide();
            }
            return $teleItemContainer
        },

        teleListViewBody: function(list_view_data, item_id) {
            var self = this;
            var itemid = item_id
            var  tele_data_calculation_type = self.tele_dashboard_data.tele_item_data[item_id].tele_data_calculation_type;
            var list_view_type = self.tele_dashboard_data.tele_item_data[item_id].tele_list_view_type
            var $teleitemBody = $(QWeb.render('tele_list_view_tmpl', {
                        list_view_data: list_view_data,
                        item_id: itemid,
                        calculation_type: tele_data_calculation_type,
                        isDrill: self.tele_dashboard_data.tele_item_data[item_id]['isDrill'],
                        list_type: list_view_type,
                    }));
            return $teleitemBody;

        },

        teleSum: function(count_1, count_2, item_info, field, target_1, $kpi_preview, kpi_data) {
            var self = this;
            var count = count_1 + count_2;
            if (field.tele_multiplier_active){
                item_info['count'] = TeleGlobalFunction._onTeleGlobalFormatter(count* field.tele_multiplier, field.tele_data_formatting, field.tele_precision_digits);
                item_info['count_tooltip'] = field_utils.format.float(count * field.tele_multiplier, Float64Array, {digits:[0,field.tele_precision_digits]});
            }else{

                item_info['count'] = TeleGlobalFunction._onTeleGlobalFormatter(count, field.tele_data_formatting, field.tele_precision_digits);
                item_info['count_tooltip'] = field_utils.format.float(parseFloat(count), Float64Array, {digits:[0,field.tele_precision_digits]});
            }
             if (field.tele_multiplier_active){
                count = count * field.tele_multiplier;
            }
            item_info['target_enable'] = field.tele_goal_enable;
            var tele_color = (target_1 - count) > 0 ? "red" : "green";
            item_info.pre_arrow = (target_1 - count) > 0 ? "down" : "up";
            item_info['tele_comparison'] = true;
            var target_deviation = (target_1 - count) > 0 ? Math.round(((target_1 - count) / target_1) * 100) : Math.round((Math.abs((target_1 - count)) / target_1) * 100);
            if (target_deviation !== Infinity) item_info.target_deviation = field_utils.format.integer(target_deviation) + "%";
            else {
                item_info.target_deviation = target_deviation;
                item_info.pre_arrow = false;
            }
            var target_progress_deviation = target_1 == 0 ? 0 : Math.round((count / target_1) * 100);
            item_info.target_progress_deviation = field_utils.format.integer(target_progress_deviation) + "%";
            $kpi_preview = $(QWeb.render("tele_kpi_template_2", item_info));
            $kpi_preview.find('.target_deviation').css({
                "color": tele_color
            });
            if (field.tele_target_view === "Progress Bar") {
                $kpi_preview.find('#tele_progressbar').val(target_progress_deviation)
            }

            return $kpi_preview;
        },

        telePercentage: function(count_1, count_2, field, item_info, target_1, $kpi_preview, kpi_data) {

            if (field.tele_multiplier_active){
                count_1 = count_1 * field.tele_multiplier;
                count_2 = count_2 * field.tele_multiplier;
            }
            var count = parseInt((count_1 / count_2) * 100);
            if (field.tele_multiplier_active){
                count = count * field.tele_multiplier;
            }
            item_info['count'] = count ? field_utils.format.integer(count) + "%" : "0%";
            item_info['count_tooltip'] = count ? count + "%" : "0%";
            item_info.target_progress_deviation = item_info['count']
            target_1 = target_1 > 100 ? 100 : target_1;
            item_info.target = target_1 + "%";
            item_info.pre_arrow = (target_1 - count) > 0 ? "down" : "up";
            var tele_color = (target_1 - count) > 0 ? "red" : "green";
            item_info['target_enable'] = field.tele_goal_enable;
            item_info['tele_comparison'] = false;
            item_info.target_deviation = item_info.target > 100 ? 100 : item_info.target;
            $kpi_preview = $(QWeb.render("tele_kpi_template_2", item_info));
            $kpi_preview.find('.target_deviation').css({
                "color": tele_color
            });
            if (field.tele_target_view === "Progress Bar") {
                if (count) $kpi_preview.find('#tele_progressbar').val(count);
                else $kpi_preview.find('#tele_progressbar').val(0);
            }

            return $kpi_preview;
        },

        renderKpi: function(item, grid) {
            var self = this;
            var field = item;
            var tele_date_filter_selection = field.tele_date_filter_selection;
            if (field.tele_date_filter_selection === "l_none") tele_date_filter_selection = self.tele_dashboard_data.tele_date_filter_selection;
            var tele_valid_date_selection = ['l_day', 't_week', 't_month', 't_quarter', 't_year'];
            var kpi_data = JSON.parse(field.tele_kpi_data);
            var count_1 = kpi_data[0].record_data;
            var count_2 = kpi_data[1] ? kpi_data[1].record_data : undefined;
            var target_1 = kpi_data[0].target;
            var target_view = field.tele_target_view,
                pre_view = field.tele_prev_view;
            var tele_rgba_background_color = self._tele_get_rgba_format(field.tele_background_color);
            var tele_rgba_button_color = self._tele_get_rgba_format(field.tele_button_color);
            var tele_rgba_font_color = self._tele_get_rgba_format(field.tele_font_color);
            if (field.tele_goal_enable) {
                var diffrence = 0.0
               if(field.tele_multiplier_active){
                    diffrence = (count_1 * field.tele_multiplier) - target_1
                }else{
                    diffrence = count_1 - target_1
                }
                var acheive = diffrence >= 0 ? true : false;
                diffrence = Math.abs(diffrence);
                var deviation = Math.round((diffrence / target_1) * 100)
                if (deviation !== Infinity) deviation = deviation ? field_utils.format.integer(deviation) + '%' : 0 + '%';
            }
            if (field.tele_previous_period && tele_valid_date_selection.indexOf(tele_date_filter_selection) >= 0) {
                var previous_period_data = kpi_data[0].previous_period;
                var pre_diffrence = (count_1 - previous_period_data);
                if (field.tele_multiplier_active){
                    var previous_period_data = kpi_data[0].previous_period * field.tele_multiplier;
                    var pre_diffrence = (count_1 * field.tele_multiplier   - previous_period_data);
                }
                var pre_acheive = pre_diffrence > 0 ? true : false;
                pre_diffrence = Math.abs(pre_diffrence);
                var pre_deviation = previous_period_data ? field_utils.format.integer(parseInt((pre_diffrence / previous_period_data) * 100)) + '%' : "100%"
            }
            item['teleIsDashboardManager'] = self.tele_dashboard_data.tele_dashboard_manager;
            item['teleIsUser'] = true;
            var tele_icon_url;
            if (field.tele_icon_select == "Custom") {
                if (field.tele_icon[0]) {
                    tele_icon_url = 'data:image/' + (self.file_type_magic_word[field.tele_icon[0]] || 'png') + ';base64,' + field.tele_icon;
                } else {
                    tele_icon_url = false;
                }
            }
//            parseInt(Math.round((count_1 / target_1) * 100)) ? field_utils.format.integer(Math.round((count_1 / target_1) * 100)) : "0"
            var target_progress_deviation = String(Math.round((count_1  / target_1) * 100));
             if(field.tele_multiplier_active){
                var target_progress_deviation = String(Math.round(((count_1 * field.tele_multiplier) / target_1) * 100));
             }
            var tele_rgba_icon_color = self._tele_get_rgba_format(field.tele_default_icon_color)
            var item_info = {
                item: item,
                id: field.id,
                count_1: TeleGlobalFunction.teleNumFormatter(kpi_data[0]['record_data'], 1),
                count_1_tooltip: kpi_data[0]['record_data'],
                count_2: kpi_data[1] ? String(kpi_data[1]['record_data']) : false,
                name: field.name ? field.name : field.tele_model_id.data.display_name,
                target_progress_deviation:target_progress_deviation,
                icon_select: field.tele_icon_select,
                default_icon: field.tele_default_icon,
                icon_color: tele_rgba_icon_color,
                target_deviation: deviation,
                target_arrow: acheive ? 'up' : 'down',
                tele_enable_goal: field.tele_goal_enable,
                tele_previous_period: tele_valid_date_selection.indexOf(tele_date_filter_selection) >= 0 ? field.tele_previous_period : false,
                target: TeleGlobalFunction.teleNumFormatter(target_1, 1),
                previous_period_data: previous_period_data,
                pre_deviation: pre_deviation,
                pre_arrow: pre_acheive ? 'up' : 'down',
                target_view: field.tele_target_view,
                pre_view: field.tele_prev_view,
                tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                tele_icon_url: tele_icon_url,
                tele_rgba_button_color:tele_rgba_button_color,

            }

            if (item_info.target_deviation === Infinity) item_info.target_arrow = false;
            item_info.target_progress_deviation = parseInt(item_info.target_progress_deviation) ? field_utils.format.integer(parseInt(item_info.target_progress_deviation)) : "0"
            if (field.tele_multiplier_active){
                item_info['count_1'] = TeleGlobalFunction._onTeleGlobalFormatter(kpi_data[0]['record_data'] * field.tele_multiplier, field.tele_data_formatting, field.tele_precision_digits);
                item_info['count_1_tooltip'] = kpi_data[0]['record_data'] * field.tele_multiplier
            }else{
                item_info['count_1'] = TeleGlobalFunction._onTeleGlobalFormatter(kpi_data[0]['record_data'], field.tele_data_formatting, field.tele_precision_digits);
            }
            item_info['target'] = TeleGlobalFunction._onTeleGlobalFormatter(kpi_data[0].target, field.tele_data_formatting, field.tele_precision_digits);
            var $kpi_preview;
            if (!kpi_data[1]) {
                if (field.tele_target_view === "Number" || !field.tele_goal_enable) {
                    $kpi_preview = $(QWeb.render("tele_kpi_template", item_info));
                } else if (field.tele_target_view === "Progress Bar" && field.tele_goal_enable) {
                    $kpi_preview = $(QWeb.render("tele_kpi_template_3", item_info));
                    $kpi_preview.find('#tele_progressbar').val(parseInt(item_info.target_progress_deviation));

                }

                if (field.tele_goal_enable) {
                    if (acheive) {
                        $kpi_preview.find(".target_deviation").css({
                            "color": "green",
                        });
                    } else {
                        $kpi_preview.find(".target_deviation").css({
                            "color": "red",
                        });
                    }
                }
                if (field.tele_previous_period && String(previous_period_data) && tele_valid_date_selection.indexOf(tele_date_filter_selection) >= 0) {
                    if (pre_acheive) {
                        $kpi_preview.find(".pre_deviation").css({
                            "color": "green",
                        });
                    } else {
                        $kpi_preview.find(".pre_deviation").css({
                            "color": "red",
                        });
                    }
                }
                if ($kpi_preview.find('.tele_target_previous').children().length !== 2) {
                    $kpi_preview.find('.tele_target_previous').addClass('justify-content-center');
                }
            } else {
                switch (field.tele_data_comparison) {
                    case "None":
                        if (field.tele_multiplier_active){
                            var count_tooltip = String(count_1 * field.tele_multiplier) + "/" + String(count_2 * field.tele_multiplier);
                            var count = String(TeleGlobalFunction.teleNumFormatter(count_1 * field.tele_multiplier, 1)) + "/" + String(TeleGlobalFunction.teleNumFormatter(count_2 * field.tele_multiplier, 1));
                            item_info['count'] = String(TeleGlobalFunction._onTeleGlobalFormatter(count_1 * field.tele_multiplier, field.tele_data_formatting, field.tele_precision_digits)) + "/" + String(TeleGlobalFunction._onTeleGlobalFormatter(count_2 * field.tele_multiplier, field.tele_data_formatting, field.tele_precision_digits));
                         }else{
                            var count_tooltip = String(count_1) + "/" + String(count_2);
                            var count = String(TeleGlobalFunction.teleNumFormatter(count_1, 1)) + "/" + String(TeleGlobalFunction.teleNumFormatter(count_2, 1));
                            item_info['count'] = String(TeleGlobalFunction._onTeleGlobalFormatter(count_1, field.tele_data_formatting, field.tele_precision_digits)) + "/" + String(TeleGlobalFunction._onTeleGlobalFormatter(count_2, field.tele_data_formatting, field.tele_precision_digits));
                         }
                        item_info['count_tooltip'] = count_tooltip;

                        item_info['target_enable'] = false;
                        $kpi_preview = $(QWeb.render("tele_kpi_template_2", item_info));
                        break;
                    case "Sum":
                        $kpi_preview = self.teleSum(count_1, count_2, item_info, field, target_1, $kpi_preview, kpi_data);
                        break;
                    case "Percentage":
                        $kpi_preview = self.telePercentage(count_1, count_2, field, item_info, target_1, $kpi_preview, kpi_data);
                        break;
                    case "Ratio":
                        var gcd = self.tele_get_gcd(Math.round(count_1), Math.round(count_2));
                        if (item.tele_data_formatting == 'exact'){
                            if (count_1 && count_2) {
                            item_info['count_tooltip'] = count_1 / gcd + ":" + count_2 / gcd;
                            item_info['count'] = field_utils.format.float(count_1 / gcd, Float64Array,{digits: [0, field.tele_precision_digits]}) + ":" + field_utils.format.float(count_2 / gcd, Float64Array, {digits: [0, field.tele_precision_digits]});
                            } else {
                            item_info['count_tooltip'] = count_1 + ":" + count_2;
                            item_info['count'] = count_1 + ":" + count_2
                                   }
                          }else{
                            if (count_1 && count_2) {
                            item_info['count_tooltip'] = count_1 / gcd + ":" + count_2 / gcd;
                            item_info['count'] = TeleGlobalFunction.teleNumFormatter(count_1 / gcd, 1) + ":" + TeleGlobalFunction.teleNumFormatter(count_2 / gcd, 1);
                            }else {
                            item_info['count_tooltip'] = (count_1) + ":" + count_2;
                            item_info['count'] = TeleGlobalFunction.teleNumFormatter(count_1, 1) + ":" + TeleGlobalFunction.teleNumFormatter(count_2, 1);
                                  }
                          }
                        item_info['target_enable'] = false;
                        $kpi_preview = $(QWeb.render("tele_kpi_template_2", item_info));
                        break;
                }
            }
            $kpi_preview.find('.tele_dashboarditem_id').css({
                "background-color": tele_rgba_background_color,
                "color": tele_rgba_font_color,
            });
            return $kpi_preview

        },

        tele_get_gcd: function(a, b) {
            return (b == 0) ? a : this.tele_get_gcd(b, a % b);
        },

        _onTeleInputChange: function(e) {
            this.teleNewDashboardName = e.target.value
        },

        onTeleDuplicateItemClick: function(e) {
            var self = this;
            var tele_item_id = $($(e.target).parentsUntil(".tele_dashboarditem_id").slice(-1)[0]).parent().attr('id');
            var dashboard_id = $($(e.target).parentsUntil(".tele_dashboarditem_id").slice(-1)[0]).find('.tele_dashboard_select').val();
            var dashboard_name = $($(e.target).parentsUntil(".tele_dashboarditem_id").slice(-1)[0]).find('.tele_dashboard_select option:selected').text();
            this._rpc({
                model: 'tele_dashboard_ninja.item',
                method: 'copy',
                args: [parseInt(tele_item_id), {
                    'tele_dashboard_ninja_board_id': parseInt(dashboard_id)
                }],
            }).then(function(result) {
                self.displayNotification({
                    title:_t("Item Duplicated"),
                    message:_t('Selected item is duplicated to ' + dashboard_name + ' .'),
                    type: 'success',
                });
                $.when(self.tele_fetch_data()).then(function () {
                    self.tele_fetch_items_data().then(function (){
                        self.teleRenderDashboard();
                    });
                });
            })
        },

        teleOnListItemInfoClick: function(e) {
            var self = this;
            var item_id = e.currentTarget.dataset.itemId;
            var item_data = self.tele_dashboard_data.tele_item_data[item_id];
            var action = {
                name: _t(item_data.name),
                type: 'ir.actions.act_window',
                res_model: e.currentTarget.dataset.model,
                domain: item_data.tele_domain || [],
                views: [
                    [false, 'list'],
                    [false, 'form']
                ],
                target: 'current',
            }
            if (e.currentTarget.dataset.listViewType === "ungrouped") {
                action['view_mode'] = 'form';
                action['views'] = [
                    [false, 'form']
                ];
                action['res_id'] = parseInt(e.currentTarget.dataset.recordId);
            } else {
                if (e.currentTarget.dataset.listType === "date_type") {
                    var domain = JSON.parse(e.currentTarget.parentElement.parentElement.dataset.domain);
                    action['view_mode'] = 'list';
                    action['context'] = {
                        'group_by': e.currentTarget.dataset.groupby,
                    };
                    action['domain'] = domain;
                } else if (e.currentTarget.dataset.listType === "relational_type") {
                    var domain = JSON.parse(e.currentTarget.parentElement.parentElement.dataset.domain);
                    action['view_mode'] = 'list';
                    action['context'] = {
                        'group_by': e.currentTarget.dataset.groupby,
                    };
                    action['domain'] = domain;
                    action['context']['search_default_' + e.currentTarget.dataset.groupby] = parseInt(e.currentTarget.dataset.recordId);
                } else if (e.currentTarget.dataset.listType === "other") {
                    var domain = JSON.parse(e.currentTarget.parentElement.parentElement.dataset.domain);
                    action['view_mode'] = 'list';
                    action['context'] = {
                        'group_by': e.currentTarget.dataset.groupby,
                    };
                    action['context']['search_default_' + e.currentTarget.dataset.groupby] = parseInt(e.currentTarget.dataset.recordId);
                    action['domain'] = domain;
                }
            }
            self.do_action(action, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });
        },

        onTeleMoveItemClick: function(e) {
            var self = this;
            var tele_item_id = $($(e.target).parentsUntil(".tele_dashboarditem_id").slice(-1)[0]).parent().attr('id');
            var dashboard_id = $($(e.target).parentsUntil(".tele_dashboarditem_id").slice(-1)[0]).find('.tele_dashboard_select').val();
            var dashboard_name = $($(e.target).parentsUntil(".tele_dashboarditem_id").slice(-1)[0]).find('.tele_dashboard_select option:selected').text();
            this._rpc({
                model: 'tele_dashboard_ninja.item',
                method: 'write',
                args: [parseInt(tele_item_id), {
                    'tele_dashboard_ninja_board_id': parseInt(dashboard_id)
                }],
            }).then(function(result) {
                self.displayNotification({
                    title:_t("Item Moved"),
                    message:_t('Selected item is moved to ' + dashboard_name + ' .'),
                    type: 'success',
                });
                $.when(self.tele_fetch_data()).then(function() {
                    $.when(self.tele_fetch_items_data()).then(function(){
                        self.tele_remove_update_interval();
                        self.teleRenderDashboard();
                        self.tele_set_update_interval();
                    });
                });
            });
        },

        _KsGetDateValues: function() {
            var self = this;

            //Setting Date Filter Selected Option in Date Filter DropDown Menu
            var date_filter_selected = self.tele_dashboard_data.tele_date_filter_selection;
            if (self.teleDateFilterSelection == 'l_none'){
                    date_filter_selected = self.teleDateFilterSelection;
//                    $('.tele_date_input_fields').addClass("tele_hide");
            }
            self.$el.find('#' + date_filter_selected).addClass("tele_date_filter_selected");
            self.$el.find('#tele_date_filter_selection').text(self.tele_date_filter_selections[date_filter_selected]);

            if (self.tele_dashboard_data.tele_date_filter_selection === 'l_custom') {
                self.$el.find('.tele_date_input_fields').removeClass("tele_hide");
                self.$el.find('.tele_date_filter_dropdown').addClass("tele_btn_first_child_radius");
            } else if (self.tele_dashboard_data.tele_date_filter_selection !== 'l_custom') {
                self.$el.find('.tele_date_input_fields').addClass("tele_hide");
            }
        },

        _onTeleClearDateValues: function(tele_l_none=false) {
            var self = this;
            self.teleDateFilterSelection = 'l_none';
            self.teleDateFilterStartDate = false;
            self.teleDateFilterEndDate = false;

            self.tele_fetch_items_data().then(function () {
                self.teleRenderDashboard();
                $('.tele_date_input_fields').addClass("tele_hide");
                $('.tele_date_filter_dropdown').removeClass("tele_btn_first_child_radius");
//                  self.teleUpdateDashboardItem()
           });

        },


        _renderDateFilterDatePicker: function() {
            var self = this;
            self.$el.find(".tele_dashboard_link").removeClass("tele_hide");
            var startDate = self.tele_dashboard_data.tele_dashboard_start_date ? moment.utc(self.tele_dashboard_data.tele_dashboard_start_date).local() : moment();
            var endDate = self.tele_dashboard_data.tele_dashboard_end_date ? moment.utc(self.tele_dashboard_data.tele_dashboard_end_date).local() : moment();

            this.teleStartDatePickerWidget = new(datepicker.DateTimeWidget)(this);

            this.teleStartDatePickerWidget.appendTo(self.$el.find(".tele_date_input_fields")).then((function() {
                this.teleStartDatePickerWidget.$el.addClass("tele_btn_middle_child o_input");
                this.teleStartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
                this.teleStartDatePickerWidget.setValue(startDate);
                this.teleStartDatePickerWidget.on("datetime_changed", this, function() {
                    self.$el.find(".apply-dashboard-date-filter").removeClass("tele_hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("tele_hide");
                });
            }).bind(this));

            this.teleEndDatePickerWidget = new(datepicker.DateTimeWidget)(this);
            this.teleEndDatePickerWidget.appendTo(self.$el.find(".tele_date_input_fields")).then((function() {
                this.teleEndDatePickerWidget.$el.addClass("tele_btn_last_child o_input");
                this.teleStartDatePickerWidget.$el.find("input").attr("placeholder", "Start Date");
                this.teleEndDatePickerWidget.setValue(endDate);
                this.teleEndDatePickerWidget.on("datetime_changed", this, function() {
                    self.$el.find(".apply-dashboard-date-filter").removeClass("tele_hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("tele_hide");
                });
            }).bind(this));

            self._KsGetDateValues();
        },

        _onTeleApplyDateFilter: function(e) {
            var self = this;
            var start_date = self.teleStartDatePickerWidget.$input.val();
            var end_date = self.teleEndDatePickerWidget.$input.val();
            $('.tele_dashboard_item_drill_up').addClass("d-none")
            if (start_date === "Invalid date") {
                alert("Invalid Date is given in Start Date.")
            } else if (end_date === "Invalid date") {
                alert("Invalid Date is given in End Date.")
            } else if (self.$el.find('.tele_date_filter_selected').attr('id') !== "l_custom") {

                self.teleDateFilterSelection = self.$el.find('.tele_date_filter_selected').attr('id');
                var res = {};
                for (const [key, value] of Object.entries(self.tele_dashboard_data.tele_item_data)) {
                    if (value.tele_dashboard_item_type != "tele_to_do") {
                        res[key] = value;
                    }
                }

                self.tele_fetch_items_data().then(function(result){
                    self.teleUpdateDashboardItem(Object.keys(res));
                    self.$el.find(".apply-dashboard-date-filter").addClass("tele_hide");
                    self.$el.find(".clear-dashboard-date-filter").addClass("tele_hide");
                });
            } else {
                if (start_date && end_date) {
                    if (moment(start_date, self.datetime_format) <= moment(end_date, self.datetime_format)) {
                        var start_date = new moment(start_date, self.datetime_format).format("YYYY-MM-DD H:m:s");
                        var end_date = new moment(end_date, self.datetime_format).format("YYYY-MM-DD H:m:s");
                        if (start_date === "Invalid date" || end_date === "Invalid date"){
                            alert(_t("Invalid Date"));
                        }else{
                            self.teleDateFilterSelection = self.$el.find('.tele_date_filter_selected').attr('id');
                            self.teleDateFilterStartDate = start_date;
                            self.teleDateFilterEndDate = end_date;

                            self.tele_fetch_items_data().then(function(result){
                                var res = {};
                                for (const [key, value] of Object.entries(self.tele_dashboard_data.tele_item_data)) {
                                    if (value.tele_dashboard_item_type != "tele_to_do") {
                                        res[key] = value;
                                    }
                                }
                                self.teleUpdateDashboardItem(Object.keys(res));
                                self.$el.find(".apply-dashboard-date-filter").addClass("tele_hide");
                                self.$el.find(".clear-dashboard-date-filter").addClass("tele_hide");
                            });
                       }

                    } else {
                        alert(_t("Start date should be less than end date"));
                    }
                } else {
                    alert(_t("Please enter start date and end date"));
                }
            }
        },

        _teleOnDateFilterMenuSelect: function(e) {
            if (e.target.id !== 'tele_date_selector_container') {
                var self = this;
                _.each($('.tele_date_filter_selected'), function($filter_options) {
                    $($filter_options).removeClass("tele_date_filter_selected")
                });
                $(e.target.parentElement).addClass("tele_date_filter_selected");
                $('#tele_date_filter_selection').text(self.tele_date_filter_selections[e.target.parentElement.id]);

                if (e.target.parentElement.id !== "l_custom") {
                    e.target.parentElement.id === "l_none" ?  self._onTeleClearDateValues(true) : self._onTeleApplyDateFilter();
                    $('.tele_date_input_fields').addClass("tele_hide");
                    $('.tele_date_filter_dropdown').removeClass("tele_btn_first_child_radius");

                } else if (e.target.parentElement.id === "l_custom") {
                    $("#tele_start_date_picker").val(null).removeClass("tele_hide");
                    $("#tele_end_date_picker").val(null).removeClass("tele_hide");
                    $('.tele_date_input_fields').removeClass("tele_hide");
                    $('.tele_date_filter_dropdown').addClass("tele_btn_first_child_radius");
                    self.$el.find(".apply-dashboard-date-filter").removeClass("tele_hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("tele_hide");
                }
            }
        },

        teleChartExportXlsCsv: function(e) {
            var chart_id = e.currentTarget.dataset.chartId;
            var name = this.tele_dashboard_data.tele_item_data[chart_id].name;
            var context = this.getContext();
            if (this.tele_dashboard_data.tele_item_data[chart_id].tele_dashboard_item_type === 'tele_list_view'){
             var params = this.teleGetParamsForItemFetch(parseInt(chart_id));
            var data = {
                "header": name,
                "chart_data": this.tele_dashboard_data.tele_item_data[chart_id].tele_list_view_data,
                "tele_item_id": chart_id,
                "tele_export_boolean": true,
                "context": context,
                'params':params,
            }
            }else{
                var data = {
                    "header": name,
                    "chart_data": this.tele_dashboard_data.tele_item_data[chart_id].tele_chart_data,
            }
            }

            framework.blockUI();
            this.getSession().get_file({
                url: '/tele_dashboard_ninja/export/' + e.currentTarget.dataset.format,
                data: {
                    data: JSON.stringify(data)
                },
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
        },

        teleChartExportPdf : function(e){
            var self = this;
            var chart_id = e.currentTarget.dataset.chartId;
            var name = this.tele_dashboard_data.tele_item_data[chart_id].name;
            var base64_image = this.chart_container[chart_id].toBase64Image();
            var $tele_el = $($(self.$el.find(".grid-stack-item[gs-id=" + chart_id + "]")).find('.tele_chart_card_body'));
            var tele_height = $tele_el.height()
           var tele_image_def = {
	            content: [{
                        image: base64_image,
                        width: 500,
                        height: tele_height,
                        }],
                images: {
                    bee: base64_image
                }
            };
             pdfMake.createPdf(tele_image_def).download(name + '.pdf');
        },

        teleItemExportJson: function(e) {
            var itemId = $(e.target).parents('.tele_dashboard_item_button_container')[0].dataset.item_id;
            var name = this.tele_dashboard_data.tele_item_data[itemId].name;
            var data = {
                'header': name,
                item_id: itemId,
            }
            framework.blockUI();
            this.getSession().get_file({
                url: '/tele_dashboard_ninja/export/item_json',
                data: {
                    data: JSON.stringify(data)
                },
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
            e.stopPropagation();
        },

        //List View pagination records
        teleLoadMoreRecords: function(e) {
            var self = this;
            var tele_intial_count = e.target.parentElement.dataset.prevOffset;
            var tele_offset = e.target.parentElement.dataset.next_offset;
            var itemId = e.currentTarget.dataset.itemId;
            var offset = self.tele_dashboard_data.tele_item_data[itemId].tele_pagination_limit;

            if (itemId in self.teleUpdateDashboard) {
                clearInterval(self.teleUpdateDashboard[itemId])
                delete self.teleUpdateDashboard[itemId];
            }
            var params = self.teleGetParamsForItemFetch(parseInt(itemId));
            this._rpc({
                model: 'tele_dashboard_ninja.board',
                method: 'tele_get_list_view_data_offset',
                context: self.getContext(),
                args: [parseInt(itemId), {
                    tele_intial_count: tele_intial_count,
                    offset: tele_offset,
                    }, parseInt(self.tele_dashboard_id), params],
            }).then(function(result) {
                var item_data = self.tele_dashboard_data.tele_item_data[itemId];
                self.tele_dashboard_data.tele_item_data[itemId]['tele_list_view_data'] = result.tele_list_view_data;
                var item_view = self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]");
                item_view.find('.card-body').empty();
                item_view.find('.card-body').append(self.renderListViewData(item_data));
                $(e.currentTarget).parents('.tele_pager').find('.tele_value').text(result.offset + "-" + result.next_offset);
                e.target.parentElement.dataset.next_offset = result.next_offset;
                e.target.parentElement.dataset.prevOffset = result.offset;
                $(e.currentTarget.parentElement).find('.tele_load_previous').removeClass('tele_event_offer_list');
                if (result.next_offset < parseInt(result.offset) + (offset - 1) || result.next_offset == item_data.tele_record_count || result.next_offset === result.limit){
                    $(e.currentTarget).addClass('tele_event_offer_list');
                }
            });
        },

        teleLoadPreviousRecords: function(e) {
            var self = this;
            var itemId = e.currentTarget.dataset.itemId;
            var offset = self.tele_dashboard_data.tele_item_data[itemId].tele_pagination_limit;
            var tele_offset =  parseInt(e.target.parentElement.dataset.prevOffset) - (offset + 1) ;
            var tele_intial_count = e.target.parentElement.dataset.next_offset;
            if (tele_offset <= 0) {
                var updateValue = self.tele_dashboard_data.tele_set_interval;
                if (updateValue) {
                    var updateinterval = setInterval(function() {
                        self.teleFetchUpdateItem(itemId)
                    }, updateValue);
                    self.teleUpdateDashboard[itemId] = updateinterval;
                }
            }
            var params = self.teleGetParamsForItemFetch(parseInt(itemId));
            this._rpc({
                model: 'tele_dashboard_ninja.board',
                method: 'tele_get_list_view_data_offset',
                context: self.getContext(),
                args: [parseInt(itemId), {
                    tele_intial_count: tele_intial_count,
                    offset: tele_offset,
                    }, parseInt(self.tele_dashboard_id), params],
            }).then(function(result) {
                var item_data = self.tele_dashboard_data.tele_item_data[itemId];
                self.tele_dashboard_data.tele_item_data[itemId]['tele_list_view_data'] = result.tele_list_view_data;
                var item_view = self.$el.find(".grid-stack-item[gs-id=" + item_data.id + "]");
                item_view.find('.card-body').empty();
                item_view.find('.card-body').append(self.renderListViewData(item_data));
                $(e.currentTarget).parents('.tele_pager').find('.tele_value').text(result.offset + "-" + result.next_offset);
                e.target.parentElement.dataset.next_offset = result.next_offset;
                e.target.parentElement.dataset.prevOffset = result.offset;
                $(e.currentTarget.parentElement).find('.tele_load_next').removeClass('tele_event_offer_list');
                if (result.offset === 1) {
                    $(e.currentTarget).addClass('tele_event_offer_list');
                }
            });
        },

    });

    core.action_registry.add('tele_dashboard_ninja', TeleDashboardNinja);

    patch(WebClient.prototype, 'tele_dn.WebClient', {
        async loadRouterState(...args) {
            var self = this;
            const sup = await this._super(...args);
            const tele_reload_menu = async (id) =>  {
                this.menuService.reload().then(() => {
                      self.menuService.selectMenu(id);
                  });
            }
            this.actionService.teleDnReloadMenu = tele_reload_menu;
            return sup;
        }

    });

    return TeleDashboardNinja;
});