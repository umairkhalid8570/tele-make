tele.define("root.widget", function (require) {
    require("web.legacySetup");
    const { ComponentAdapter } = require("web.TwlCompatibility");

    const { Component } = twl;

    return new ComponentAdapter(null, { Component }); // for its method _trigger_up
});
