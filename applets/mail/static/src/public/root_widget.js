/**
 * This module exists so that web_tour can use it as the parent of the
 * TourManager so it can get access to _trigger_up.
 */
tele.define("root.widget", function (require) {
    const { ComponentAdapter } = require("web.TwlCompatibility");
    const { Component } = twl;
    return new ComponentAdapter(null, { Component });
});
