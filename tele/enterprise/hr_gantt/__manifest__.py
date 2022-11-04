# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employees in Gantt',
    'category': 'Hidden',
    'summary': 'Employees in Gantt',
    'version': '1.0',
    'description': """ """,
    'depends': ['hr', 'web_gantt'],
    'auto_install': True,
    'license': 'TEEL-1',
    'assets': {
        'web.assets_backend': [
            'hr_gantt/static/src/js/**/*',
        ],
        'web.qunit_suite_tests': [
            'hr_gantt/static/tests/**/*',
        ],
        'web.assets_qweb': [
            'hr_gantt/static/src/xml/**/*',
        ],
    }
}
