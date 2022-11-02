/** @tele-module **/

import { ComponentAdapter } from 'web.TwlCompatibility';

export default class ViewsWidgetAdapter extends ComponentAdapter {
    setup() {
        super.setup(...arguments);
        // Overwrite the TWL/legacy env with the WOWL's one.
        this.env = twl.Component.env;
    }

    get widgetArgs() {
        const {model, view, additionalContext, params, mode, view_type} = this.props.data;
        return [
            model,
            view,
            additionalContext,
            params,
            mode,
            view_type
        ];
    }
}
