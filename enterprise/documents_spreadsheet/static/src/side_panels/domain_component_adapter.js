/** @tele-module */

import { ComponentAdapter } from "web.TwlCompatibility";

/**
 * ComponentAdapter to allow using DomainSelector in a twl Component
 */
export default class DomainComponentAdapter extends ComponentAdapter {
    setup() {
        this.env = twl.Component.env;
    }
    get widgetArgs() {
        return [this.props.model, this.props.domain, { readonly: true, filters: {} }];
    }
}
