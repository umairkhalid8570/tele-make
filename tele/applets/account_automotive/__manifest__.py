# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
{
    'name': 'Accounting/Automotive bridge',
    'category': 'Accounting/Accounting',
    'summary': 'Manage accounting with automotives',
    'description': "",
    'version': '1.0',
    'depends': ['automotive', 'account'],
    'data': [
        'data/automotive_service_type_data.xml',
        'views/account_move_views.xml',
        'views/automotive_vehicle_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'LGPL-3',
}
