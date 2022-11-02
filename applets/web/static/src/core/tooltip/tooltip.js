/** @tele-module **/

const { Component } = twl;

export class Tooltip extends Component {}
Tooltip.template = "web.Tooltip";
Tooltip.props = {
    tooltip: { type: String, optional: true },
    template: { type: String, optional: true },
    info: { optional: true },
};
