tele.define('tele_dashboard_builder_list.tele_dashboard_builder_list_view_preview', function(require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');

    var QWeb = core.qweb;
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var _t = core._t;

    var TeleListViewPreview = AbstractField.extend({
        supportedFieldTypes: ['char'],

        resetOnAnyFieldChange: true,

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            var l10n = _t.database.parameters;
            this.date_format = time.strftime_to_moment_format(_t.database.parameters.date_format)
            this.date_format = this.date_format.replace(/\bYY\b/g, "YYYY");
            this.datetime_format = time.strftime_to_moment_format((_t.database.parameters.date_format + ' ' + l10n.time_format))
            this.state = {};
        },

        _render: function() {
            this.$el.empty()
            var rec = this.recordData;
            if (rec.tele_dashboard_item_type === 'tele_list_view') {
                if (rec.tele_list_view_type == "ungrouped") {
                    if (rec.tele_list_view_fields.count !== 0) {
                        this.teleRenderListView();
                    } else {
                        this.$el.append($('<div>').text("Select Fields to show in list view."));
                    }
                } else if (rec.tele_list_view_type == "grouped") {
                    if (rec.tele_list_view_group_fields.count !== 0 && rec.tele_chart_relation_groupby) {
                        if (rec.tele_chart_groupby_type === 'relational_type' || rec.tele_chart_groupby_type === 'selection' || rec.tele_chart_groupby_type === 'other' || rec.tele_chart_groupby_type === 'date_type' && rec.tele_chart_date_groupby) {
                            this.teleRenderListView();
                        } else {
                            this.$el.append($('<div>').text("Select Group by Date to show list data."));
                        }

                    } else {
                        this.$el.append($('<div>').text("Select Fields and Group By to show in list view."));

                    }
                }
            }
        },

        teleRenderListView: function() {
            var self = this;
            var field = this.recordData;
            var tele_list_view_name;
            var list_view_data = JSON.parse(field.tele_list_view_data);
            var count = field.tele_record_count;
            if (field.name) tele_list_view_name = field.name;
            else if (field.tele_model_name) tele_list_view_name = field.tele_model_id.data.display_name;
            else tele_list_view_name = "Name";
            if (field.tele_list_view_type === "ungrouped" && list_view_data) {
                var index_data = list_view_data.date_index;
                if (index_data){
                    for (var i = 0; i < index_data.length; i++) {
                        for (var j = 0; j < list_view_data.data_rows.length; j++) {
                            var index = index_data[i]
                            var date = list_view_data.data_rows[j]["data"][index]
                            if (date){
                             if( list_view_data.fields_type[index] === 'date'){
                                    list_view_data.data_rows[j]["data"][index] = moment(new Date(date)).format(this.date_format) , {}, {timezone: false};
                             } else{
                                list_view_data.data_rows[j]["data"][index] = field_utils.format.datetime(moment(moment(date).utc(true)._d), {}, {
                                timezone: false
                            });
                            }

                            }else {list_view_data.data_rows[j]["data"][index] = "";}
                        }
                    }
                }
            }

            if (field.tele_list_view_data) {
                var data_rows = list_view_data.data_rows;
                if (data_rows){
                    for (var i = 0; i < list_view_data.data_rows.length; i++) {
                    for (var j = 0; j < list_view_data.data_rows[0]["data"].length; j++) {
                        if (typeof(list_view_data.data_rows[i].data[j]) === "number" || list_view_data.data_rows[i].data[j]) {
                            if (typeof(list_view_data.data_rows[i].data[j]) === "number") {
                                list_view_data.data_rows[i].data[j] = field_utils.format.float(list_view_data.data_rows[i].data[j], Float64Array, {digits: [0, field.tele_precision_digits]})
                            }
                        } else {
                            list_view_data.data_rows[i].data[j] = "";
                        }
                    }
                }
                }
            } else list_view_data = false;
            count = list_view_data && field.tele_list_view_type === "ungrouped" ? count - list_view_data.data_rows.length : false;
            count = count ? count <=0 ? false : count : false;
            var $listViewContainer = $(QWeb.render('tele_list_view_container', {
                tele_list_view_name: tele_list_view_name,
                list_view_data: list_view_data,
                count: count,
                layout: self.recordData.tele_list_view_layout,
            }));
            if (!this.recordData.tele_show_records === true) {
                $listViewContainer.find('#tele_item_info').hide();
            }
            this.$el.append($listViewContainer);
        },


    });
    registry.add('tele_dashboard_list_view_preview', TeleListViewPreview);

    return {
        TeleListViewPreview: TeleListViewPreview,
    };

});