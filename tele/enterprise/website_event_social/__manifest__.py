# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.


{
    'name': 'Schedule push notifications on attendees',
    'category': 'Marketing/Events',
    'sequence': 1020,
    'version': '1.1',
    'summary': 'Bridge module to push notifications to event attendees',
    'website': 'https://www.tele.studio/app/events',
    'description': "",
    'depends': [
        'website_event',
        'social_push_notifications',
    ],
    'data': [
        'views/event_event_views.xml',
        'views/event_templates_registration.xml'
    ],
    'demo': [
    ],
    'application': False,
    'installable': True,
    'auto_install': True,
    'assets': {
        'web.assets_frontend': [
            'website_event_social/static/**/*',
        ],
    },
    'license': 'TEEL-1',
}
