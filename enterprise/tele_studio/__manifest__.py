# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
{
    'name': "Tele-Studio",
    'summary': "Create and customize your Tele apps",
    'website': 'https://www.tele.studio/app/studio',
    'description': """
Studio - Customize Tele
=======================

This addon allows the user to customize most element of the user interface, in a
simple and graphical way. It has two main features:

* create a new application (add module, top level menu item, and default action)
* customize an existing application (edit menus, actions, views, translations, ...)

Note: Only the admin user is allowed to make those customizations.
""",
    'category': 'Customizations/Studio',
    'sequence': 75,
    'version': '1.0',
    'depends': [
        'base_automation',
        'base_import_module',
        'mail',
        'web',
        'web_enterprise',
        'web_editor',
        'web_map',
        'web_gantt',
        'sms',
    ],
    'data': [
        'views/assets.xml',
        'views/actions.xml',
        'views/base_import_module_view.xml',
        'views/ir_actions_report_xml.xml',
        'views/ir_model_data.xml',
        'views/studio_approval_views.xml',
        'data/mail_templates.xml',
        'wizard/base_module_uninstall_view.xml',
        'security/ir.model.access.csv',
        'security/studio_security.xml',
    ],
    'application': True,
    'license': 'TEEL-1',
    'assets': {
        'web.assets_backend': [
            'tele_studio/static/src/systray_item/**/*.js',
            'tele_studio/static/src/studio_service.js',
            'tele_studio/static/src/utils.js',
            'tele_studio/static/src/tours/**/*.js',

            'tele_studio/static/src/legacy/js/approval_component.js',
            'tele_studio/static/src/legacy/scss/approval_component.scss',
            'tele_studio/static/src/legacy/js/bus.js',
            'tele_studio/static/src/legacy/js/views/renderers/form_renderer.js',
            'tele_studio/static/src/legacy/js/views/renderers/list_renderer_eager.js',
            'tele_studio/static/src/legacy/js/views/controllers/form_controller.js',
            'tele_studio/static/src/legacy/studio_legacy_service.js',
            'tele_studio/static/src/home_menu/**/*.js',
        ],
        'web.assets_backend_prod_only': [
            'tele_studio/static/src/client_action/studio_action_loader.js',
            'tele_studio/static/src/client_action/app_creator/app_creator_shortcut.js',
        ],
        # This bundle is lazy loaded: it is loaded when studio is opened for the first time
        'tele_studio.studio_assets': [
            'tele_studio/static/src/client_action/**/*.js',
            ('remove', 'tele_studio/static/src/client_action/studio_action_loader.js'),
            ('remove', 'tele_studio/static/src/client_action/app_creator/app_creator_shortcut.js'),
            'tele_studio/static/src/legacy/action_editor_main.js',
            'tele_studio/static/src/legacy/edit_menu_adapter.js',
            'tele_studio/static/src/legacy/new_model_adapter.js',

            'tele_studio/static/src/legacy/js/py.js',
            'tele_studio/static/src/legacy/js/edit_menu.js',
            'tele_studio/static/src/legacy/js/new_model.js',
            'tele_studio/static/src/legacy/js/common_menu_dialog.js',
            'tele_studio/static/src/legacy/js/common/**/*.js',
            'tele_studio/static/src/legacy/js/reports/**/*.js',
            'tele_studio/static/src/legacy/js/views/abstract_view.js',
            'tele_studio/static/src/legacy/js/views/action_editor.js',
            'tele_studio/static/src/legacy/js/views/action_editor_sidebar.js',
            'tele_studio/static/src/legacy/js/views/action_editor_view.js',
            'tele_studio/static/src/legacy/js/views/view_components.js',
            'tele_studio/static/src/legacy/js/views/view_editor_manager.js',
            'tele_studio/static/src/legacy/js/views/view_editor_sidebar.js',
            'tele_studio/static/src/legacy/js/views/renderers/search_renderer.js',
            'tele_studio/static/src/legacy/js/views/renderers/list_renderer_lazy.js',
            'tele_studio/static/src/legacy/js/views/view_editors/**/*.js',

            ('include', 'web._assets_helpers'),
            'web/static/lib/bootstrap/scss/_variables.scss',
            'tele_studio/static/src/client_action/variables.scss',
            'tele_studio/static/src/client_action/mixins.scss',
            'tele_studio/static/src/client_action/**/*.scss',

            'tele_studio/static/src/legacy/scss/icons.scss',
            'tele_studio/static/src/legacy/scss/action_editor.scss',
            'tele_studio/static/src/legacy/scss/form_editor.scss',
            'tele_studio/static/src/legacy/scss/kanban_view.scss',
            'tele_studio/static/src/legacy/scss/kanban_editor.scss',
            'tele_studio/static/src/legacy/scss/list_editor.scss',
            'tele_studio/static/src/legacy/scss/new_field_dialog.scss',
            'tele_studio/static/src/legacy/scss/report_editor.scss',
            'tele_studio/static/src/legacy/scss/report_editor_manager.scss',
            'tele_studio/static/src/legacy/scss/report_editor_sidebar.scss',
            'tele_studio/static/src/legacy/scss/report_kanban_view.scss',
            'tele_studio/static/src/legacy/scss/search_editor.scss',
            'tele_studio/static/src/legacy/scss/sidebar.scss',
            'tele_studio/static/src/legacy/scss/view_editor_manager.scss',
            'tele_studio/static/src/legacy/scss/xml_editor.scss',
        ],
        'web.assets_tests': [
            'tele_studio/static/tests/legacy/tours/**/*',
        ],
        'tele_studio.report_assets': [
            ('include', 'web._assets_helpers'),
            'web/static/lib/bootstrap/scss/_variables.scss',
            'tele_studio/static/src/legacy/scss/report_iframe.scss',
        ],
        'web.qunit_suite_tests': [
            # In tests we don't want to lazy load this
            # And we don't want to push them into any other test suite either
            # as web.tests_assets would
            ('include', 'tele_studio.studio_assets'),
            'tele_studio/static/tests/mock_server.js',
            'tele_studio/static/tests/helpers.js',
            'tele_studio/static/tests/*.js',
            'tele_studio/static/tests/legacy/action_editor_action_tests.js',
            'tele_studio/static/tests/legacy/edit_menu_tests.js',
            'tele_studio/static/tests/legacy/new_model_tests.js',
            'tele_studio/static/tests/legacy/mock_server.js',
            'tele_studio/static/tests/legacy/test_utils.js',
            'tele_studio/static/tests/legacy/reports/**/*.js',
            'tele_studio/static/tests/legacy/views/**/*.js',
        ],
        'web.assets_qweb': [
            'tele_studio/static/src/home_menu/home_menu.xml',
            'tele_studio/static/src/**/*.xml',
        ],
    }
}
