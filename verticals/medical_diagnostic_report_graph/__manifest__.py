# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Diagnostic Report Graph",
    "summary": """
        This applets enables to add a graph to the medical diagnostic report""",
    "version": "1.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Tele Community",
    "website": "www.creublanca.es",
    "depends": ["medical_diagnostic_report"],
    "data": [
        "views/medical_diagnostic_report_template.xml",
        "views/medical_diagnostic_report.xml",
        "reports/medical_diagnostic_report_base.xml",
        "reports/medical_diagnostic_report_template.xml",
    ],
    "demo": ["demo/auditory_test.xml", "demo/visual_acuity_test.xml"],
    "external_dependencies": {
        "python": ["bokeh", "phantomjs", "numpy", "pandas"]
    },
}
