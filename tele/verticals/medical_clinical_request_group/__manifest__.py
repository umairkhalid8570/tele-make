
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Clinical Request Group",
    "summary": "Medical request group",
    "version": "1.0.1.0.0",
    "author": "Tele Community",
    "category": "Medical",
    "website": "https://health.tele.studio",
    "license": "LGPL-3",
    "depends": ["medical_clinical", "medical_workflow"],
    "data": [
        "data/ir_sequence_data.xml",
        "data/medical_workflow.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "views/medical_request_view.xml",
        "views/medical_request_group_view.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
