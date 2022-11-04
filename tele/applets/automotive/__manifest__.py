# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Automotive',
    'version' : '0.1',
    'sequence': 185,
    'category': 'Human Resources/Automotive',
    'website' : 'https://www.tele.studio/app/automotive',
    'summary' : 'Manage your automotive and track car costs',
    'description' : """
Vehicle, leasing, insurances, cost
==================================
With this module, Tele helps you managing all your vehicles, the
contracts associated to those vehicle as well as services, costs
and many other features necessary to the management of your automotive
of vehicle(s)

Main Features
-------------
* Add vehicles to your automotive
* Manage contracts for vehicles
* Reminder when a contract reach its expiration date
* Add services, odometer values for all vehicles
* Show all costs associated to a vehicle or to a type of service
* Analysis graph for costs
""",
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/automotive_security.xml',
        'security/ir.model.access.csv',
        'views/automotive_vehicle_model_views.xml',
        'views/automotive_vehicle_views.xml',
        'views/automotive_vehicle_cost_views.xml',
        'views/automotive_board_view.xml',
        'views/mail_activity_views.xml',
        'views/res_config_settings_views.xml',
        'data/automotive_cars_data.xml',
        'data/automotive_data.xml',
        'data/mail_data.xml',
    ],

    'demo': ['data/automotive_demo.xml'],

    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'automotive/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
