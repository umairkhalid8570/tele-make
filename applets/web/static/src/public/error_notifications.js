/** @tele-module */
// This module makes it so that some errors only display a notification instead of an error dialog

import { registry } from "@web/core/registry";
import { teleExceptionTitleMap } from "@web/core/errors/error_dialogs";
import { _t } from "@web/core/l10n/translation";

teleExceptionTitleMap.forEach((title, exceptionName) => {
    registry.category("error_notifications").add(exceptionName, {
        title: title,
        type: "warning",
        sticky: true
    });
});

const sessionExpired = {
    title: _t("Tele Session Expired"),
    message: _t("Your Tele session expired. The current page is about to be refreshed."),
    buttons: [
        {
            text: _t("Ok"),
            click: () => window.location.reload(true),
            close: true
        }
    ]
};

registry
    .category("error_notifications")
    .add("tele.http.SessionExpiredException", sessionExpired)
    .add("werkzeug.exceptions.Forbidden", sessionExpired)
    .add("504", {
        title: _t("Request timeout"),
        message: _t(
            "The operation was interrupted. This usually means that the current operation is taking too much time."
        )
    });
