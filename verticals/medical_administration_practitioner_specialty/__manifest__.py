# Copyright 2017 LasLabs Inc.

# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration Practitioner Specialty",
    "version": "1.0.1.0.0",
    "author": "Tele INC",
    "category": "Medical",
    "website": "https://health.tele.studio",
    "license": "LGPL-3",
    "depends": [
        "medical_administration_practitioner",
        "medical_terminology_sct",
    ],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/sct_data.xml",
        "views/res_partner_views.xml",
        "views/medical_specialty.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
