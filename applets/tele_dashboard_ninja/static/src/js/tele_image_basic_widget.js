tele.define('tele_dashboard_ninja_list.tele_image_basic_widget', function(require) {
    "use strict";

    var core = require('web.core');
    var basic_fields = require('web.basic_fields');
    var core = require('web.core');
    var registry = require('web.field_registry');

    var QWeb = core.qweb;

    var TeleImageWidget = basic_fields.FieldBinaryImage.extend({

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.teleSelectedIcon = false;
            this.tele_icon_set = ['home', 'puzzle-piece', 'clock-o', 'comments-o', 'car', 'calendar', 'calendar-times-o', 'bar-chart', 'commenting-o', 'star-half-o', 'address-book-o', 'tachometer', 'search', 'money', 'line-chart', 'area-chart', 'pie-chart', 'check-square-o', 'users', 'shopping-cart', 'truck', 'user-circle-o', 'user-plus', 'sun-o', 'paper-plane', 'rss', 'gears', 'check', 'book'];
        },

        template: 'TeleFieldBinaryImage',

        events: _.extend({}, basic_fields.FieldBinaryImage.prototype.events, {
            'click .tele_icon_container_list': 'tele_icon_container_list',
            'click .tele_image_widget_icon_container': 'tele_image_widget_icon_container',
            'click .tele_icon_container_open_button': 'tele_icon_container_open_button',
            'click .tele_fa_icon_search': 'tele_fa_icon_search',
            'keyup .tele_modal_icon_input': 'tele_modal_icon_input_enter',
        }),

        _render: function() {
            var tele_self = this;
            var url = this.placeholder;
            if (tele_self.value) {
                tele_self.$('> img').remove();
                tele_self.$('> span').remove();
                $('<span>').addClass('fa fa-' + tele_self.recordData.tele_default_icon + ' fa-5x').appendTo(tele_self.$el).css('color', 'black');
            } else {
                var $img = $(QWeb.render("FieldBinaryImage-img", {
                    widget: this,
                    url: url
                }));
                tele_self.$('> img').remove();
                tele_self.$('> span').remove();
                tele_self.$el.prepend($img);
            }

            var $tele_icon_container_modal = $(QWeb.render('tele_icon_container_modal_template', {
                tele_fa_icons_set: tele_self.tele_icon_set
            }));

            $tele_icon_container_modal.prependTo(tele_self.$el);
        },

        //This will show modal box on clicking on open icon button.
        tele_image_widget_icon_container: function(e) {
            $('#tele_icon_container_modal_id').modal({
                show: true,
            });

        },


        tele_icon_container_list: function(e) {
            var self = this;
            self.teleSelectedIcon = $(e.currentTarget).find('span').attr('id').split('.')[1]
            _.each($('.tele_icon_container_list'), function(selected_icon) {
                $(selected_icon).removeClass('tele_icon_selected');
            });

            $(e.currentTarget).addClass('tele_icon_selected')
            $('.tele_icon_container_open_button').show()
        },

        //Imp :  Hardcoded for svg file only. If different file, change this code to dynamic.
        tele_icon_container_open_button: function(e) {
            var tele_self = this;
            tele_self._setValue(tele_self.teleSelectedIcon);
        },

        tele_fa_icon_search: function(e) {
            var self = this
            self.$el.find('.tele_fa_search_icon').remove()
            var tele_fa_icon_name = self.$el.find('.tele_modal_icon_input')[0].value
            if (tele_fa_icon_name.slice(0, 3) === "fa-") {
                tele_fa_icon_name = tele_fa_icon_name.slice(3)
            }
            var tele_fa_icon_render = $('<div>').addClass('tele_icon_container_list tele_fa_search_icon')
            $('<span>').attr('id', 'tele.' + tele_fa_icon_name.toLocaleLowerCase()).addClass("fa fa-" + tele_fa_icon_name.toLocaleLowerCase() + " fa-4x").appendTo($(tele_fa_icon_render))
            $(tele_fa_icon_render).appendTo(self.$el.find('.tele_icon_container_grid_view'))
        },

        tele_modal_icon_input_enter: function(e) {
            var tele_self = this
            if (e.keyCode == 13) {
                tele_self.$el.find('.tele_fa_icon_search').click()
            }
        },
    });

    registry.add('tele_image_widget', TeleImageWidget);

    return {
        TeleImageWidget: TeleImageWidget,
    };
});