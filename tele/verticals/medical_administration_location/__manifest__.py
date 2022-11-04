# Copyright 2017 LasLabs Inc.

# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration Location",
    "version": "1.0.1.0.0",
    "category": "Medical",
    "website": "https://health.tele.studio",
    "author": "LasLabs, Creu Blanca, Eficent,"
    "Tele Community",
    "license": "LGPL-3",
    "depends": ["medical_administration"],
    "data": [
        "security/medical_security.xml",
        "data/ir_sequence_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/medical_patient.xml",
        "views/medical_menu.xml",
    ],
    "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "application": False,
}
