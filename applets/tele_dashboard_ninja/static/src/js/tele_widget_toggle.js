tele.define('tele_dashboard_ninja_list.tele_widget_toggle', function (require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var QWeb = core.qweb;

    var TeleWidgetToggle = AbstractField.extend({

        supportedFieldTypes: ['char'],

        events: _.extend({}, AbstractField.prototype.events, {
            'change .tele_toggle_icon_input': 'tele_toggle_icon_input_click',
        }),

        _render: function () {
            var self = this;
            self.$el.empty();


            var $view = $(QWeb.render('tele_widget_toggle'));
            if (self.value) {
                $view.find("input[value='" + self.value + "']").prop("checked", true);
            }
            this.$el.append($view)

            if (this.mode === 'readonly') {
                this.$el.find('.tele_select_dashboard_item_toggle').addClass('tele_not_click');
            }
        },

        tele_toggle_icon_input_click: function (e) {
            var self = this;
            self._setValue(e.currentTarget.value);
        }
    });

    var TeleWidgetToggleKPI = AbstractField.extend({

        supportedFieldTypes: ['char'],

        events: _.extend({}, AbstractField.prototype.events, {
            'change .tele_toggle_icon_input': 'tele_toggle_icon_input_click',
        }),

        _render: function () {
            var self = this;
            self.$el.empty();
            var $view = $(QWeb.render('tele_widget_toggle_kpi'));

            if (self.value) {
                $view.find("input[value='" + self.value + "']").prop("checked", true);
            }
            this.$el.append($view)

            if (this.mode === 'readonly') {
                this.$el.find('.tele_select_dashboard_item_toggle').addClass('tele_not_click');
            }
        },
        tele_toggle_icon_input_click: function (e) {
            var self = this;
            self._setValue(e.currentTarget.value);
        }
    });

    var TeleWidgetToggleKpiTarget = AbstractField.extend({
        supportedFieldTypes: ['char'],

        events: _.extend({}, AbstractField.prototype.events, {
            'change .tele_toggle_icon_input': 'tele_toggle_icon_input_click',
        }),

        _render: function () {
            var self = this;
            self.$el.empty();


            var $view = $(QWeb.render('tele_widget_toggle_kpi_target_view'));
            if (self.value) {
                $view.find("input[value='" + self.value + "']").prop("checked", true);
            }
            this.$el.append($view)

            if (this.mode === 'readonly') {
                this.$el.find('.tele_select_dashboard_item_toggle').addClass('tele_not_click');
            }
        },

        tele_toggle_icon_input_click: function (e) {
            var self = this;
            self._setValue(e.currentTarget.value);
        }
    });

    registry.add('tele_widget_toggle', TeleWidgetToggle);
    registry.add('tele_widget_toggle_kpi', TeleWidgetToggleKPI);
    registry.add('tele_widget_toggle_kpi_target', TeleWidgetToggleKpiTarget);
    return {
        TeleWidgetToggle: TeleWidgetToggle,
        TeleWidgetToggleKPI: TeleWidgetToggleKPI,
        TeleWidgetToggleKpiTarget :KsWidgetToggleKpiTarget
    };


});