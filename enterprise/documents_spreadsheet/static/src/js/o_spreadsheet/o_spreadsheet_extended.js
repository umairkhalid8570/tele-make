/** @tele-module alias=documents_spreadsheet.spreadsheet_extended */

import "./registries/autofill";
import "./registries/filter_component";
import "./registries/menu_item_registry";
import "./registries/pivot_functions";
import "./registries/list_functions";
import "./registries/tele_menu_link_cell";
import "./../collaborative/operational_transform";

import { _t } from "web.core";
import spreadsheet from "./o_spreadsheet_loader";

/** Core */
import PivotPlugin from "./plugins/core/pivot_plugin";
import ListPlugin from "./plugins/core/list_plugin";
import FiltersPlugin from "./plugins/core/filters_plugin";

/** UI */
import PivotStructurePlugin from "./plugins/ui/pivot_structure_plugin";
import PivotTemplatePlugin from "documents_spreadsheet.PivotTemplatePlugin";
import PivotAutofillPlugin from "./plugins/ui/pivot_autofill_plugin";
import ListStructurePlugin from "./plugins/ui/list_structure_plugin";


/** Side panels */
import PivotSidePanel from "../../side_panels/pivot/pivot_list_side_panel";
import ListingAllSidePanel from "../../side_panels/list/listing_all_side_panel";
import ListAutofillPlugin from "./plugins/ui/list_autofill_plugin";
import FiltersEvaluationPlugin from "./plugins/ui/filters_evaluation_plugin";

const { coreTypes, invalidateEvaluationCommands, readonlyAllowedCommands } = spreadsheet;
const { corePluginRegistry, uiPluginRegistry, sidePanelRegistry } = spreadsheet.registries;

corePluginRegistry.add("telePivotPlugin", PivotPlugin);
corePluginRegistry.add("teleListPlugin", ListPlugin);
corePluginRegistry.add("teleFiltersPlugin", FiltersPlugin);

uiPluginRegistry.add("telePivotStructurePlugin", PivotStructurePlugin);
uiPluginRegistry.add("teleListStructurePlugin", ListStructurePlugin);
uiPluginRegistry.add("telePivotAutofillPlugin", PivotAutofillPlugin);
uiPluginRegistry.add("teleListAutofillPlugin", ListAutofillPlugin);
uiPluginRegistry.add("telePivotTemplatePlugin", PivotTemplatePlugin);
uiPluginRegistry.add("teleFiltersEvaluationPlugin", FiltersEvaluationPlugin);

coreTypes.add("ADD_PIVOT");
coreTypes.add("ADD_PIVOT_FORMULA");
coreTypes.add("ADD_GLOBAL_FILTER");
coreTypes.add("EDIT_GLOBAL_FILTER");
coreTypes.add("REMOVE_GLOBAL_FILTER");
coreTypes.add("ADD_TELE_LIST");
coreTypes.add("ADD_TELE_LIST_FORMULA");

invalidateEvaluationCommands.add("ADD_GLOBAL_FILTER");
invalidateEvaluationCommands.add("EDIT_GLOBAL_FILTER");
invalidateEvaluationCommands.add("REMOVE_GLOBAL_FILTER");
invalidateEvaluationCommands.add("SET_GLOBAL_FILTER_VALUE");

readonlyAllowedCommands.add("SET_GLOBAL_FILTER_VALUE");
readonlyAllowedCommands.add("ADD_PIVOT_DOMAIN");
readonlyAllowedCommands.add("ADD_LIST_DOMAIN");

sidePanelRegistry.add("PIVOT_PROPERTIES_PANEL", {
    title: () => _t("Pivot properties"),
    Body: PivotSidePanel,
});
sidePanelRegistry.add("LIST_PROPERTIES_PANEL", {
    title: () => _t("List properties"),
    Body: ListingAllSidePanel,
});

export default spreadsheet;
