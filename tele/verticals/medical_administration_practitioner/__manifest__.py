# Copyright 2017 LasLabs Inc.

# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration Practitioner",
    "version": "1.0.1.0.0",
    "author": "Tele INC"
    "Tele Community",
    "category": "Medical",
    "website": "https://health.tele.studio",
    "license": "LGPL-3",
    "depends": ["medical_administration"],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/medical_role.xml",
        "views/res_config_settings_views.xml",
        "views/medical_role.xml",
        "views/res_partner_views.xml",
        "views/medical_menu.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
