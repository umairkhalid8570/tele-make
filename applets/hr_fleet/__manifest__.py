# -*- encoding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
{
    'name': 'Automotive History',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Get history of driven cars by employees',
    'description': "",
    'depends': ['hr', 'automotive'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_automotive_security.xml',
        'views/employee_views.xml',
        'views/automotive_vehicle_views.xml',
        'views/automotive_vehicle_cost_views.xml',
        'wizard/hr_departure_wizard_views.xml',
    ],
    'demo': [
        'data/hr_automotive_demo.xml',
    ],
    'auto_install': True,
    'license': 'LGPL-3',
}
