tele.define('tele_dashboard_ninja.quick_edit_view', function(require) {
    "use strict";

    var core = require('web.core');
    var Widget = require("web.Widget");
    var _t = core._t;
    var QWeb = core.qweb;
    var data = require('web.data');
    var QuickCreateFormView = require('web.QuickCreateFormView');
    var AbstractAction = require('web.AbstractAction');
    const session = require('web.session');

    var QuickEditView = Widget.extend({

        template: 'teleQuickEditViewOption',

        events: {
            'click .tele_quick_edit_action': 'teleOnQuickEditViewAction',
        },

        init: function(parent, options) {
            this._super.apply(this, arguments);
            this.teleDashboardController = parent;

            this.teleOriginalItemData = $.extend({}, options.item);
            this.item = options.item;
            this.item_name = options.item.name;

        },


        willStart: function() {
            var self = this;
            return $.when(this._super()).then(function() {
                return self._teleCreateController();
            });
        },

        _teleCreateController: function() {
            var self = this;

            self.context = $.extend({}, session.user_context);
            self.context['form_view_ref'] = 'tele_dashboard_ninja.item_quick_edit_form_view';
            self.context['res_id'] = this.item.id;
            self.res_model = "tele_dashboard_ninja.item";
            self.dataset = new data.DataSet(this, this.res_model, self.context);
            var def = self.loadViews(this.dataset.model, self.context, [
                [false, 'list'],
                [false, 'form']
            ], {});
            return $.when(def).then(function(fieldsViews) {
                self.formView = new QuickCreateFormView(fieldsViews.form, {
                    context: self.context,
                    modelName: self.res_model,
                    userContext: self.getSession().user_context,
                    currentId: self.item.id,
                    index: 0,
                    mode: 'edit',
                    footerToButtons: true,
                    default_buttons: false,
                    withControlPanel: false,
                    ids: [self.item.id],
                });
                var def2 = self.formView.getController(self);
                return $.when(def2).then(function(controller) {
                    self.controller = controller;
                    self.controller._confirmChange = self._confirmChange.bind(self);
                });
            });
        },

        //This Function is replacing Controllers to intercept in between to fetch changed data and update our item view.
        _confirmChange: function(id, fields, e) {
            if (e.name === 'discard_changes' && e.target.reset) {
                // the target of the discard event is a field widget.  In that
                // case, we simply want to reset the specific field widget,
                // not the full view
                return e.target.reset(this.controller.model.get(e.target.dataPointID), e, true);
            }

            var state = this.controller.model.get(this.controller.handle);
            this.controller.renderer.confirmChange(state, id, fields, e);
            return this.tele_Update_item();
        },

        tele_Update_item: function() {
            var self = this;
            var teleChanges = this.controller.renderer.state.data;

            if (teleChanges['name']) this.item['name'] = teleChanges['name'];

            self.item['tele_font_color'] = teleChanges['tele_font_color'];
            self.item['tele_icon_select'] = teleChanges['tele_icon_select'];
            self.item['tele_icon'] = teleChanges['tele_icon'];
            self.item['tele_background_color'] = teleChanges['tele_background_color'];
            self.item['tele_default_icon_color'] = teleChanges['tele_default_icon_color'];
            self.item['tele_layout'] = teleChanges['tele_layout'];
            self.item['tele_record_count'] = teleChanges['tele_record_count'];

            if (teleChanges['tele_list_view_data']) self.item['tele_list_view_data'] = teleChanges['tele_list_view_data'];

            if (teleChanges['tele_chart_data']) self.item['tele_chart_data'] = teleChanges['tele_chart_data'];

            if (teleChanges['tele_kpi_data']) self.item['tele_kpi_data'] = teleChanges['tele_kpi_data'];

            if (teleChanges['tele_list_view_type']) self.item['tele_list_view_type'] = teleChanges['tele_list_view_type'];

            if (teleChanges['tele_chart_item_color']) self.item['tele_chart_item_color'] = teleChanges['tele_chart_item_color'];

            self.teleUpdateItemView();

        },

        start: function() {
            var self = this;
            this._super.apply(this, arguments);

        },

        renderElement: function() {
            var self = this;
            self._super.apply(this, arguments);
            self.controller.appendTo(self.$el.find(".tele_item_field_info"));

            self.trigger('canBeRendered', {});
        },

        teleUpdateItemView: function() {
            var self = this;
            self.teleDashboardController.teleUpdateDashboardItem([self.item.id]);
            self.item_el = $.find('#' + self.item.id + '.tele_dashboarditem_id');

        },

        teleDiscardChanges: function() {
            var self = this;
            self.teleDashboardController.teleFetchUpdateItem(self.item.id);
            self.destroy();
        },


        teleOnQuickEditViewAction: function(e) {
            var self = this;
            self.need_reset = false;
            var options = {
                'need_item_reload': false
            }
            if (e.currentTarget.dataset['teleItemAction'] === 'saveItemInfo') {
                this.controller.saveRecord().then(function() {
                    self.teleDiscardChanges();
                })
            } else if (e.currentTarget.dataset['teleItemAction'] === 'fullItemInfo') {
                this.trigger('openFullItemForm', {});
            } else {
                self.teleDiscardChanges();
            }
        },

        destroy: function(options) {
            this.trigger('canBeDestroyed', {});
            this.controller.destroy();
            this._super();
        },
    });


    return {
        QuickEditView: QuickEditView,
    };
});