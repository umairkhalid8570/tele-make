# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Automotive Dashboard',
    'version' : '0.1',
    'sequence': 200,
    'category': 'Human Resources/Automotive',
    'website' : 'https://www.tele.studio/app/automotive',
    'summary' : 'Dashboard for automotive',
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
        'automotive', 'web_dashboard'
    ],
    'data': [
        'views/automotive_board_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': True,
    'uninstall_hook': 'uninstall_hook',
    'license': 'TEEL-1',
}
