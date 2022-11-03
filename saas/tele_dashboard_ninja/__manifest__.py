# -*- coding: utf-8 -*-
{
	'name': 'Dashboard Ninja',

	'summary': """
Tele Dashboard Ninja gives you a wide-angle view of your business that you might have missed. Get smart visual data with interactive and engaging dashboards for your Tele ERP.  Tele Dashboard, CRM Dashboard, Inventory Dashboard, Sales Dashboard, Account Dashboard, Invoice Dashboard, Revamp Dashboard, Best Dashboard, Tele Best Dashboard, Tele Apps Dashboard, Best Ninja Dashboard, Analytic Dashboard, Pre-Configured Dashboard, Create Dashboard, Beautiful Dashboard, Customized Robust Dashboard, Predefined Dashboard, Multiple Dashboards, Advance Dashboard, Beautiful Powerful Dashboards, Chart Graphs Table View, All In One Dynamic Dashboard, Accounting Stock Dashboard, Pie Chart Dashboard, Modern Dashboard, Dashboard Studio, Dashboard Builder, Dashboard Designer, Tele Studio.  Revamp your Tele Dashboard like never before! It is one of the best dashboard tele apps in the market.
""",

	'description': """

""",

	'author': 'Tele INC',

	'license': 'TPL-1',

	'maintainer': 'Tele INC',

	'category': 'Tools',

	'version': '1.0.1.1.5',

	'support': 'sales@tele.studio',

	'images': ['static/description/banner.gif'],

	'depends': ['base', 'web', 'base_setup', 'bus'],

	'data': ['security/ir.model.access.csv', 'security/tele_security_groups.xml', 'data/tele_default_data.xml', 'views/tele_dashboard_ninja_view.xml', 'views/tele_dashboard_ninja_item_view.xml', 'views/tele_dashboard_action.xml', 'views/tele_import_dashboard_view.xml', 'wizard/tele_create_dashboard_wiz_view.xml', 'wizard/tele_duplicate_dashboard_wiz_view.xml'],

	'demo': ['demo/tele_dashboard_ninja_demo.xml'],

	'assets': {'web.assets_backend': ['tele_dashboard_ninja/static/src/css/tele_dashboard_ninja.scss', 'tele_dashboard_ninja/static/src/css/tele_dashboard_ninja_item.css', 'tele_dashboard_ninja/static/src/css/tele_icon_container_modal.css', 'tele_dashboard_ninja/static/src/css/tele_dashboard_item_theme.css', 'tele_dashboard_ninja/static/src/css/tele_dn_filter.css', 'tele_dashboard_ninja/static/src/css/tele_toggle_icon.css', 'tele_dashboard_ninja/static/src/css/tele_dashboard_options.css', 'tele_dashboard_ninja/static/src/js/tele_global_functions.js', 'tele_dashboard_ninja/static/src/js/tele_dashboard_ninja.js', 'tele_dashboard_ninja/static/src/js/tele_to_do_dashboard.js', 'tele_dashboard_ninja/static/src/js/tele_filter_props.js', 'tele_dashboard_ninja/static/src/js/tele_color_picker.js', 'tele_dashboard_ninja/static/src/js/tele_dashboard_ninja_item_preview.js', 'tele_dashboard_ninja/static/src/js/tele_image_basic_widget.js', 'tele_dashboard_ninja/static/src/js/tele_dashboard_item_theme.js', 'tele_dashboard_ninja/static/src/js/tele_widget_toggle.js', 'tele_dashboard_ninja/static/src/js/tele_import_dashboard.js', 'tele_dashboard_ninja/static/src/js/tele_domain_fix.js', 'tele_dashboard_ninja/static/src/js/tele_quick_edit_view.js', 'tele_dashboard_ninja/static/src/js/tele_dashboard_ninja_kpi_preview.js', 'tele_dashboard_ninja/static/src/js/tele_date_picker.js', 'tele_dashboard_ninja/static/lib/css/gridstack.min.css', 'tele_dashboard_ninja/static/lib/js/gridstack-h5.js', 'tele_dashboard_ninja/static/lib/js/Chart.bundle.min.js', 'tele_dashboard_ninja/static/src/css/tele_dashboard_ninja_pro.css', 'tele_dashboard_ninja/static/src/css/tele_to_do_item.css', 'tele_dashboard_ninja/static/src/js/tele_dashboard_ninja_graph_preview.js', 'tele_dashboard_ninja/static/src/js/tele_dashboard_ninja_list_view_preview.js', 'tele_dashboard_ninja/static/src/js/tele_to_do_preview.js'], 'web.assets_qweb': ['tele_dashboard_ninja/static/src/xml/**/*']},

	'uninstall_hook': 'uninstall_hook',
}
