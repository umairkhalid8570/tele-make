# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

{
    'name': 'TeleBot',
    'version': '1.2',
    'category': 'Productivity/Connect',
    'summary': 'Add TeleBot in discussions',
    'description': "",
    'website': 'https://www.tele.studio/app/connect',
    'depends': ['mail'],
    'auto_install': True,
    'installable': True,
    'application': False,
    'data': [
        'views/res_users_views.xml',
        'data/mailbot_data.xml',
    ],
    'demo': [
        'data/mailbot_demo.xml',
    ],
    'assets': {
        'mail.assets_discuss_public': [
            'mail_bot/static/src/models/*/*.js',
        ],
        'web.assets_backend': [
            'mail_bot/static/src/models/*/*.js',
            'mail_bot/static/src/scss/telebot_style.scss',
        ],
        'web.tests_assets': [
            'mail_bot/static/tests/**/*',
        ],
        'web.qunit_suite_tests': [
            'mail_bot/static/src/models/*/tests/*.js',
        ],
    },
    'license': 'LGPL-3',
}
