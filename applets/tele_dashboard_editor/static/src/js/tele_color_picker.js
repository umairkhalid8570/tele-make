tele.define('tele_dashboard_editor_list.tele_color_picker', function(require) {
    "use strict";

    require('web.dom_ready');

    var registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');

    var QWeb = core.qweb;

    //Widget for color picker being used in dashboard item create view.
    //TODO : This color picker functionality can be improved a lot.
    var TeleColorPicker = AbstractField.extend({

        supportedFieldTypes: ['char'],

        events: _.extend({}, AbstractField.prototype.events, {
            'change.spectrum .tele_color_picker': '_teleOnColorChange',
            'change .tele_color_opacity': '_teleOnOpacityChange',
            'input .tele_color_opacity': '_teleOnOpacityInput'
        }),

        jsLibs: [
            '/tele_dashboard_editor/static/lib/js/spectrum.js'
        ],
        cssLibs: [
            '/tele_dashboard_editor/static/lib/css/spectrum.css',
        ],

        _render: function() {
            this.$el.empty();
            var tele_color_value = '#376CAE';
            var tele_color_opacity = '0.99';
            if (this.value) {
                tele_color_value = this.value.split(',')[0];
                tele_color_opacity = this.value.split(',')[1];
            };
            var $view = $(QWeb.render('tele_color_picker_opacity_view', {
                tele_color_value: tele_color_value,
                tele_color_opacity: tele_color_opacity
            }));

            this.$el.append($view)

            this.$el.find(".tele_color_picker").spectrum({
                color: tele_color_value,
                showInput: true,
                hideAfterPaletteSelect: true,

                clickoutFiresChange: true,
                showInitial: true,
                preferredFormat: "rgb",
            });

            if (this.mode === 'readonly') {
                this.$el.find('.tele_color_picker').addClass('tele_not_click');
                this.$el.find('.tele_color_opacity').addClass('tele_not_click');
                this.$el.find('.tele_color_picker').spectrum("disable");
            } else {
                this.$el.find('.tele_color_picker').spectrum("enable");
            }
        },



        _teleOnColorChange: function(e, tinycolor) {
            this._setValue(tinycolor.toHexString().concat("," + this.value.split(',')[1]));
        },

        _teleOnOpacityChange: function(event) {
            this._setValue(this.value.split(',')[0].concat("," + event.currentTarget.value));
        },

        _teleOnOpacityInput: function(event) {
            var self = this;
            var color;
            if (self.name == "tele_background_color") {
                color = $('.tele_db_item_preview_color_picker').css("background-color")
                $('.tele_db_item_preview_color_picker').css("background-color", self.get_color_opacity_value(color, event.currentTarget.value))

                color = $('.tele_db_item_preview_l2').css("background-color")
                $('.tele_db_item_preview_l2').css("background-color", self.get_color_opacity_value(color, event.currentTarget.value))

            } else if (self.name == "tele_default_icon_color") {
                color = $('.tele_dashboard_icon_color_picker > span').css('color')
                $('.tele_dashboard_icon_color_picker > span').css('color', self.get_color_opacity_value(color, event.currentTarget.value))
            } else if (self.name == "tele_font_color") {
                color = $('.tele_db_item_preview').css("color")
                color = $('.tele_db_item_preview').css("color", self.get_color_opacity_value(color, event.currentTarget.value))
            }
        },

        get_color_opacity_value: function(color, val) {
            if (color) {
                return color.replace(color.split(',')[3], val + ")");
            } else {
                return false;
            }
        },


    });
    registry.add('tele_color_dashboard_picker', TeleColorPicker);

    return {
        TeleColorPicker: TeleColorPicker
    };

});