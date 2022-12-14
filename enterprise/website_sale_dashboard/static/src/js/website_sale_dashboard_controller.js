tele.define('website_sale_dashboard.WebsiteSaleDashboardController', function (require) {
"use strict";

var core = require('web.core');
var DashboardController = require('web_dashboard.DashboardController');

var qweb = core.qweb;

var WebsiteSaleDashboardController = DashboardController.extend({

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     * @param {jQuery} [$node]
     */
    renderButtons: function () {
        this.$buttons = $('<div>');
        this.$buttons.append(qweb.render("website.GoToButtons", {widget: this}));
        this.$buttons.prependTo(this.$el);
    },

});

return WebsiteSaleDashboardController;

});
