/** @tele-module **/

import { registry } from "@web/core/registry";
import { _lt } from "@web/core/l10n/translation";

registry
    .category("tele_studio.editor_tabs")
    .add('website', { name: _lt("Website"), action: "action_tele_studio_form" });
