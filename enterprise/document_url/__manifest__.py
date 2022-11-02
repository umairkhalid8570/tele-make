# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2020 Tecnativa - Manuel Calero
{
    "name": "URL attachment",
    "version": "1.0.1.0.0",
    "category": "Tools",
    "author": "Tecnativa, Tele-Community",
    "website": "https://github.com/tele-studio/tele",
    "license": "AGPL-3",
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "view/document_url_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "document_url/static/src/js/url.esm.js",
        ],
        "web.assets_qweb": [
            "document_url/static/src/xml/url.xml",
        ],
    },
    "installable": True,
}
