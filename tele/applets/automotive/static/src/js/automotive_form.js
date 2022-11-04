tele.define('automotive.AutomotiveForm', function(require) {
    "use strict";

    const FormController = require('web.FormController');
    const FormView = require('web.FormView');
    const viewRegistry = require('web.view_registry');
    const Dialog = require('web.Dialog');

    const core = require('web.core');
    const _t = core._t;

    const AutomotiveFormController = FormController.extend({
        /**
         * @override
         * @private
         **/
        _getActionMenuItems: function (state) {
            if (!this.hasActionMenus || this.mode === 'edit') {
                return null;
            }
            var menuItems = this._super.apply(this, arguments);
            var archiveAction = _.find(menuItems.items.other, (actionItem) => {return actionItem.description === _t("Archive");});
            if (archiveAction) {
                archiveAction.callback = () => {
                    Dialog.confirm(this, _t("Each Services and contracts of this vehicle will be considered as Archived. Are you sure that you want to archive this record?"), {
                        confirm_callback: () => this._toggleArchiveState(true),
                    });
                };
            }
            return menuItems;
        },

    });

    var AutomotiveFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: AutomotiveFormController,
        }),
    });

    viewRegistry.add('automotive_form', AutomotiveFormView);

    return AutomotiveFormView;
});
