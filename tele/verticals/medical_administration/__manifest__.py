
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration",
    "summary": "Medical administration base module",
    "version": "1.0.1.0.0",
    "author": "Tele Community",
    "website": "https://health.tele.studio",
    "category": "Medical",
    "license": "LGPL-3",
    "depends": ["medical_base"],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/medical_menu.xml",
        "views/medical_patient_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": True,
}
