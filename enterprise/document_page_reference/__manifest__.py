# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Page Reference",
    "summary": """
        Include references on document pages""",
    "version": "1.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Tele-Community",
    "website": "https://github.com/tele-studio/tele",
    "depends": ["document_page", "web_editor"],
    "data": [
        "views/document_page.xml",
        "views/report_document_page.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "document_page_reference/static/src/js/**/*",
        ],
    },
    "maintainers": ["etobella"],
}
