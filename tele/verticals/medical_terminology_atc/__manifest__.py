
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical ATC Codification",
    "summary": "Medical codification base",
    "version": "1.0.1.0.0",
    "author": "Tele Community",
    "category": "Medical",
    "website": "https://health.tele.studio",
    "license": "LGPL-3",
    "depends": ["medical_terminology"],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/atc_data.xml",
        "views/medical_atc_concept_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
