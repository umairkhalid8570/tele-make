/** @tele-module **/

import { ComponentAdapter } from "web.TwlCompatibility";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

import FormManager from "website_studio.FormManager";

export class FormManagerAdapter extends ComponentAdapter {
    constructor(parent, props) {
        props.Component = FormManager;
        super(...arguments);
        this.studio = useService("studio");
        this.env = twl.Component.env;
    }

    get widgetArgs() {
        return [this.props.action, { action: this.studio.editedAction }];
    }
}

registry.category("actions").add("action_tele_studio_form", FormManagerAdapter);
