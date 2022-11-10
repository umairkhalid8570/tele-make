tele.define('tele_dashboard_builder_list.tele_to_do_preview', function(require) {
    "use strict";

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');

    var QWeb = core.qweb;
    var field_utils = require('web.field_utils');

    var TeleToDOViewPreview = AbstractField.extend({
        supportedFieldTypes: ['char'],

        resetOnAnyFieldChange: true,

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.state = {};
        },

        _render: function() {
            var self = this;
            this.$el.empty()
            var rec = self.recordData;
            var tele_rgba_font_color;
            if (rec.tele_dashboard_item_type === 'tele_to_do') {
                    self.teleRenderToDoView(rec);
                }
        },

          _tele_get_rgba_format: function(val) {
            var rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
            rgba = rgba.map(function(v) {
                return parseInt(v, 16)
            }).join(",");
            return "rgba(" + rgba + "," + val.split(',')[1] + ")";
        },

        teleRenderToDoView: function(rec) {
            var self = this;
            var tele_header_color = self._tele_get_rgba_format(rec.tele_header_bg_color);
            var tele_font_color = self._tele_get_rgba_format(rec.tele_font_color);
            var tele_rgba_button_color = self._tele_get_rgba_format(rec.tele_button_color);
             var list_to_do_data = {}
                   if (rec.tele_to_do_data){
                        list_to_do_data = JSON.parse(rec.tele_to_do_data)
                   }
            var $todoViewContainer = $(QWeb.render('tele_to_do_container', {

                tele_to_do_view_name: rec.name ? rec.name : 'Name',
                to_do_view_data: list_to_do_data,
            }));
            $todoViewContainer.find('.tele_card_header').addClass('tele_bg_to_color').css({"background-color": tele_header_color });
            $todoViewContainer.find('.tele_card_header').addClass('tele_bg_to_color').css({"color": tele_font_color + ' !important' });
            $todoViewContainer.find('.tele_li_tab').addClass('tele_bg_to_color').css({"color": tele_font_color + ' !important' });
            $todoViewContainer.find('.tele_chart_heading').addClass('tele_bg_to_color').css({"color": tele_font_color + ' !important' });
            this.$el.append($todoViewContainer);
        },


    });
    registry.add('tele_dashboard_to_do_preview', TeleToDOViewPreview);

    return {
        TeleToDOViewPreview: TeleToDOViewPreview,
    };

});