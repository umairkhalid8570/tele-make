tele.define('tele_dashboard_editor_list.tele_dashboard_kpi_preview', function(require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var utils = require('web.utils');
    var TeleGlobalFunction = require('tele_dashboard_editor.TeleGlobalFunction');

    var Qweb = core.qweb;

    var TeleKpiPreview = AbstractField.extend({

        supportedFieldTypes: ['char'],

        resetOnAnyFieldChange: true,

        file_type_magic_word: {
            '/': 'jpg',
            'R': 'gif',
            'i': 'png',
            'P': 'svg+xml',
        },

        //        Number Formatter into shorthand function
        teleNumFormatter: function(num, digits) {
            var negative;
            var si = [{
                    value: 1,
                    symbol: ""
                },
                {
                    value: 1E3,
                    symbol: "k"
                },
                {
                    value: 1E6,
                    symbol: "M"
                },
                {
                    value: 1E9,
                    symbol: "G"
                },
                {
                    value: 1E12,
                    symbol: "T"
                },
                {
                    value: 1E15,
                    symbol: "P"
                },
                {
                    value: 1E18,
                    symbol: "E"
                }
            ];
            if (num < 0) {
                num = Math.abs(num)
                negative = true
            }
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length - 1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }
            if (negative) {
                return "-" + (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            } else {
                return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            }
        },
        teleNumIndianFormatter: function(num, digits) {
            var negative;
            var si = [{
                value: 1,
                symbol: ""
            },
            {
                value: 1E3,
                symbol: "Th"
            },
            {
                value: 1E5,
                symbol: "Lakh"
            },
            {
                value: 1E7,
                symbol: "Cr"
            },
            {
                value: 1E9,
                symbol: "Arab"
            }
            ];
            if (num < 0) {
                num = Math.abs(num)
                negative = true
            }
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length - 1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }
            if (negative) {
                return "-" + (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            } else {
                return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
            }

        },

        _render: function() {
            this.$el.empty();
            if (this.recordData.tele_model_id && this.recordData.tele_dashboard_item_type === "tele_kpi") {
                if (!this.recordData.tele_model_id_2) {
                    if (!(this.recordData.tele_record_count_type === 'count')) {
                        if (this.recordData.tele_record_field) {
                            this.renderKpi();
                        } else {
                            this.$el.append("Select a Record field ")
                        }
                    } else {
                        this.renderKpi();
                    }
                } else {
                    if (!(this.recordData.tele_record_count_type_2 === 'count') && !(this.recordData.tele_record_count_type === 'count')) {
                        if (this.recordData.tele_record_field_2 && this.recordData.tele_record_field) {
                            this.renderKpi();
                        } else {
                            this.$el.append("Select a Record fields ")
                        }
                    } else if (!(this.recordData.tele_record_count_type_2 === 'count') && (this.recordData.tele_record_count_type === 'count')) {
                        if (this.recordData.tele_record_field_2) {
                            this.renderKpi();
                        } else {
                            this.$el.append("Select a Record field")
                        }
                    } else if ((this.recordData.tele_record_count_type_2 === 'count') && !(this.recordData.tele_record_count_type === 'count')) {
                        if (this.recordData.tele_record_field) {
                            this.renderKpi();
                        } else {
                            this.$el.append("Select a Record field")
                        }
                    } else {
                        this.renderKpi();
                    }
                }
            } else {
                this.$el.append("Select a Model first")
            }
        },
        teleSum: function(count_1, count_2, item_info, field, target_1, $kpi_preview, kpi_data) {
            var self = this;
            var count = count_1 + count_2
            if (field.tele_multiplier_active){
                item_info['count'] = TeleGlobalFunction._onTeleGlobalFormatter(count* field.tele_multiplier, field.tele_data_format, field.tele_precision_digits);
                item_info['count_tooltip'] = field_utils.format.float(count * field.tele_multiplier, Float64Array, {digits: [0, field.tele_precision_digits]});
            }else{

                item_info['count'] = TeleGlobalFunction._onTeleGlobalFormatter(count, field.tele_data_format, field.tele_precision_digits, field.tele_precision_digits);
                item_info['count_tooltip'] = field_utils.format.float(count, Float64Array, {digits: [0, field.tele_precision_digits]});
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
                item_info.pre_arrow = false;
                item_info.target_deviation = target_deviation;
            }
            var target_progress_deviation = target_1 == 0 ? 0 : Math.round((count / target_1) * 100);
            item_info.target_progress_deviation = field_utils.format.integer(target_progress_deviation) + "%";
            $kpi_preview = $(Qweb.render("tele_kpi_preview_template_2", item_info));
            $kpi_preview.find('.target_deviation').css({
                "color": tele_color
            });
            if (this.recordData.tele_target_view === "Progress Bar") {
                $kpi_preview.find('#tele_progressbar').val(target_progress_deviation)
            }
            return $kpi_preview
        },
        telePercentage: function(count_1, count_2, field, item_info, target_1, $kpi_preview) {
            if (field.tele_multiplier_active){
                count_1 = count_1 * field.tele_multiplier;
                count_2 = count_2 * field.tele_multiplier;
            }
            var count = parseInt((count_1 / count_2) * 100);
            if (field.tele_multiplier_active){
                count = count * field.tele_multiplier;
            }
            if (!count) count = 0;
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
            $kpi_preview = $(Qweb.render("tele_kpi_preview_template_2", item_info));
            $kpi_preview.find('.target_deviation').css({
                "color": tele_color
            });
            if (this.recordData.tele_target_view === "Progress Bar") {
                $kpi_preview.find('#tele_progressbar').val(count)
            }
            return $kpi_preview;
        },
        renderKpi: function() {
            var self = this;
            var field = this.recordData;
            var kpi_data = JSON.parse(field.tele_kpi_data);
//            if (field.tele_multiplier_active){
//                var count_1 = kpi_data[0].record_data * field.tele_multiplier;
//                var count_2 = kpi_data[1] * field.tele_multiplier ? kpi_data[1].record_data : undefined;
//                var target_1 = kpi_data[0].target * field.tele_multiplier;
//            }else{
                var count_1 = kpi_data[0].record_data;
                var count_2 = kpi_data[1] ? kpi_data[1].record_data : undefined;
                var target_1 = kpi_data[0].target;
//            }
            var tele_valid_date_selection = ['l_day', 't_week', 't_month', 't_quarter', 't_year'];
            var target_view = field.tele_target_view,
                pre_view = field.tele_prev_view;
            var tele_rgba_background_color = self._get_rgba_format(field.tele_background_color);
            var tele_rgba_font_color = self._get_rgba_format(field.tele_font_color)

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
            if (field.tele_previous_period && tele_valid_date_selection.indexOf(field.tele_date_filter_selection) >= 0) {
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
             var target_progress_deviation = String(Math.round((count_1  / target_1) * 100));
             if(field.tele_multiplier_active){
                var target_progress_deviation = String(Math.round(((count_1 * field.tele_multiplier) / target_1) * 100));
             }
            var tele_rgba_icon_color = self._get_rgba_format(field.tele_default_icon_color)
            var item_info = {
                count_1: self.teleNumFormatter(kpi_data[0]['record_data'], 1),
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
                tele_previous_period: tele_valid_date_selection.indexOf(field.tele_date_filter_selection) >= 0 ? field.tele_previous_period : false,
                target: self.teleNumFormatter(target_1, 1),
                previous_period_data: previous_period_data,
                pre_deviation: pre_deviation,
                pre_arrow: pre_acheive ? 'up' : 'down',
                target_view: field.tele_target_view,
            }

            if (item_info.target_deviation === Infinity) item_info.target_arrow = false;
            item_info.target_progress_deviation = parseInt(item_info.target_progress_deviation) ? field_utils.format.integer(parseInt(item_info.target_progress_deviation)) : "0"
            if (field.tele_icon) {
                if (!utils.is_bin_size(field.tele_icon)) {
                    // Use magic-word technique for detecting image type
                    item_info['img_src'] = 'data:image/' + (self.file_type_magic_word[field.tele_icon[0]] || 'png') + ';base64,' + field.tele_icon;
                } else {
                    item_info['img_src'] = session.url('/web/image', {
                        model: self.model,
                        id: JSON.stringify(self.res_id),
                        field: "tele_icon",
                        // unique forces a reload of the image when the record has been updated
                        unique: field_utils.format.datetime(self.recordData.__last_update).replace(/[^0-9]/g, ''),
                    });
                }
            }
            if (field.tele_multiplier_active){
                item_info['count_1'] = TeleGlobalFunction._onTeleGlobalFormatter(kpi_data[0]['record_data'] * field.tele_multiplier, field.tele_data_format, field.tele_precision_digits);
                item_info['count_1_tooltip'] = kpi_data[0]['record_data'] * field.tele_multiplier
            }else{
                item_info['count_1'] = TeleGlobalFunction._onTeleGlobalFormatter(kpi_data[0]['record_data'], field.tele_data_format, field.tele_precision_digits);
            }
            item_info['target'] = TeleGlobalFunction._onTeleGlobalFormatter(kpi_data[0].target, field.tele_data_format, field.tele_precision_digits);


            var $kpi_preview;
            if (!kpi_data[1]) {
                if (target_view === "Number" || !field.tele_goal_enable) {
                    $kpi_preview = $(Qweb.render("tele_kpi_preview_template", item_info));
                } else if (target_view === "Progress Bar" && field.tele_goal_enable) {
                    $kpi_preview = $(Qweb.render("tele_kpi_preview_template_3", item_info));
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
                if (field.tele_previous_period && String(previous_period_data) && tele_valid_date_selection.indexOf(field.tele_date_filter_selection) >= 0) {
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
                if ($kpi_preview.find('.row').children().length !== 2) {
                    $kpi_preview.find('.row').children().addClass('text-center');
                }
            } else {
                switch (field.tele_data_comparison) {
                    case "None":
                         if (field.tele_multiplier_active){
                            var count_tooltip = String(count_1 * field.tele_multiplier) + "/" + String(count_2 * field.tele_multiplier);
                            var count = String(self.teleNumFormatter(count_1 * field.tele_multiplier, 1)) + "/" + String(self.teleNumFormatter(count_2 * field.tele_multiplier, 1));
                            item_info['count'] = String(TeleGlobalFunction._onTeleGlobalFormatter(count_1 * field.tele_multiplier, field.tele_data_format, field.tele_precision_digits)) + "/" + String(TeleGlobalFunction._onTeleGlobalFormatter(count_2 * field.tele_multiplier, field.tele_data_format, field.tele_precision_digits));
                         }else{
                            var count_tooltip = String(count_1) + "/" + String(count_2);
                            var count = String(self.teleNumFormatter(count_1, 1)) + "/" + String(self.teleNumFormatter(count_2, 1));
                            item_info['count'] = String(TeleGlobalFunction._onTeleGlobalFormatter(count_1, field.tele_data_format, field.tele_precision_digits)) + "/" + String(TeleGlobalFunction._onTeleGlobalFormatter(count_2, field.tele_data_format, field.tele_precision_digits));
                         }

                        item_info['count_tooltip'] = count_tooltip
                        item_info['target_enable'] = false;
                        $kpi_preview = $(Qweb.render("tele_kpi_preview_template_2", item_info));
                        break;
                    case "Sum":
                        $kpi_preview = self.teleSum(count_1, count_2, item_info, field, target_1, $kpi_preview, kpi_data);
                        break;
                    case "Percentage":
                        $kpi_preview = self.telePercentage(count_1, count_2, field, item_info, target_1, $kpi_preview);
                        break;
                    case "Ratio":
                        var gcd = self.tele_get_gcd(Math.round(count_1), Math.round(count_2));
                        if (field.tele_data_format == 'exact'){
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
                        $kpi_preview = $(Qweb.render("tele_kpi_preview_template_2", item_info));
                        break;
                }
            }
            $kpi_preview.css({
                "background-color": tele_rgba_background_color,
                "color": tele_rgba_font_color,
            });
            this.$el.append($kpi_preview);
        },

        tele_get_gcd: function(a, b) {
            return (b == 0) ? a : this.tele_get_gcd(b, a % b);
        },

        _get_rgba_format: function(val) {
            var rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
            rgba = rgba.map(function(v) {
                return parseInt(v, 16)
            }).join(",");
            return "rgba(" + rgba + "," + val.split(',')[1] + ")";
        }

    });
    registry.add('tele_dashboard_kpi_preview', TeleKpiPreview);
    return {
        TeleKpiPreview: TeleKpiPreview
    };

});