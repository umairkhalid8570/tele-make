# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

{
    'name': 'Assets/Automotive bridge',
    'category': 'Accounting/Accounting',
    'summary': 'Manage assets with automotives',
    'description': "",
    'version': '1.0',
    'depends': ['account_automotive', 'account_asset'],
    'data': [
        'views/account_asset_views.xml',
        'views/account_move_views.xml',
    ],
    'license': 'TEEL-1',
    'auto_install': True,
}
