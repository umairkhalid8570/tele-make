tele.define("documents_spreadsheet.model_selector_widget", function (require) {
    const { ComponentAdapter } = require("web.TwlCompatibility");

    class ModelSelectorWidgetAdapter extends ComponentAdapter {
        setup() {
            this.env = twl.Component.env;
        }
        /**
         * @override
         */
        get widgetArgs() {
            return [
                "ir.model",
                this.props.modelID,
                [["model", "in", this.props.models]],
            ];
        }
    }

    return { ModelSelectorWidgetAdapter };
});
