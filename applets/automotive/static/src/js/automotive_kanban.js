tele.define('automotive.automotive_kanban', function (require) {
    'use strict';

    const KanbanRecord = require('web.KanbanRecord');

    KanbanRecord.include({

        /**
         * @override
         * @private
         */
        _openRecord() {
            if (this.modelName === 'automotive.vehicle.model.brand' && this.$(".oe_kanban_automotive_model").length) {
                this.$('.oe_kanban_automotive_model').first().click();
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});
