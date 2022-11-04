
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration Encounter",
    "summary": "Add Encounter concept",
    "version": "1.0.1.0.0",
    "author": "Tele Community",
    "category": "Medical",
    "website": "https://health.tele.studio",
    "license": "LGPL-3",
    "depends": ["medical_administration", "medical_administration_location"],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "views/medical_encounter_view.xml",
        "views/medical_menu.xml",
        "views/medical_patient.xml",
        "security/ir.model.access.csv",
        "data/medical_encounter_sequence.xml",
    ],
    "installable": True,
    "auto_install": False,
}
