/** @tele-module **/

import { Dialog } from "../core/dialog/dialog";
import { patch } from "@web/core/utils/patch";
import { useEffect } from "@web/core/utils/hooks";
import TwlDialog from "web.TwlDialog";

/**
 * This is a patch of the new Dialog class.
 * Its purpose is to inform the old "active/inactive" mechanism.
 */
patch(Dialog.prototype, "Legacy Adapted Dialog", {
    setup() {
        this._super();
        useEffect(
            () => {
                TwlDialog.display(this);
                return () => TwlDialog.hide(this);
            },
            () => []
        );
    },
});
