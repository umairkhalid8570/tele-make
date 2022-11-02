/* @tele-module */

import widgetRegistry from "web.widget_registry";
import widgetRegistryTwl from "web.widgetRegistry";
import { registry } from "@web/core/registry";
import { useEffect } from "@web/core/utils/hooks";
import { ComponentAdapter } from "web.TwlCompatibility";
import { decodeObjectForTemplate } from "./dashboard_compiler/compile_helpers";

/**
 * A Component that supports rendering `<widget />` tags in a view arch
 * It should have minimum legacy support that is:
 * - getting the legacy widget class from the legacy registry
 * - instanciating a legacy widget
 * - passing to it a "legacy node", which is a representation of the arch's node
 * It supports instancing components from the "view_widgets" new registry
 */
export class ViewWidget extends twl.Component {
    setup() {
        this.wowlEnv = this.env;
        this.renderId = 1;
        useEffect(() => {
            this.renderId++;
        });
        const widgetName = this.props.widgetName;
        const Widget = registry.category("view_widgets").get(widgetName, null);
        if (!Widget) {
            this.isLegacyTwl = true;
            this.env = twl.Component.env;
        }
        this.Widget = Widget || widgetRegistryTwl.get(widgetName) || widgetRegistry.get(widgetName);
        this.isLegacy = !(this.Widget instanceof twl.Component);
    }

    get widgetProps() {
        if (!this.isLegacyTwl) {
            return this.props;
        } else {
            throw new Error("To implement ....");
        }
    }

    get widgetArgs() {
        const record = this.props.model._legacyRecord_;
        const node = this.props._legacyNode_
            ? decodeObjectForTemplate(this.props._legacyNode_)
            : {};
        node.name = this.props.widgetName;
        if (this.props.title) {
            node.attrs = Object.assign(node.attrs || {}, { title: this.props.title });
        }
        return [record, node];
    }
}
ViewWidget.template = twl.tags.xml/*xml*/ `<t>
    <ComponentAdapter t-if="isLegacy" Component="Widget" widgetArgs="widgetArgs" t-key="renderId" class="o_widget" />
    <t t-else="" t-component="Widget" t-props="widgetProps" class="o_widget" />
</t>
`;
ViewWidget.components = { ComponentAdapter };
