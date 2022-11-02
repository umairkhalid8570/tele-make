/** @tele-module **/

import mobile from "web_mobile.core";
import { download } from "@web/core/network/download";

const _download = download._download;

download._download = async function (options) {
    if (mobile.methods.downloadFile) {
        if (tele.csrf_token) {
            options.csrf_token = tele.csrf_token;
        }
        mobile.methods.downloadFile(options);
        return Promise.resolve();
    } else {
        return _download.apply(this, arguments);
    }
};
