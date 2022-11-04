
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Medication",
    "summary": "Medical medication base",
    "version": "1.0.1.0.0",
    "author": "Tele Community",
    "category": "Medical",
    "website": "https://health.tele.studio",
    "license": "LGPL-3",
    "depends": [
        "medical_administration",
        "medical_terminology_sct",
        "medical_terminology_atc",
        "product",
        "stock",
    ],
    "data": [
        "security/medical_security.xml",
        "data/sct_data.xml",
        "views/medical_menu.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": ["demo/sct_data.xml", "demo/medication.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
