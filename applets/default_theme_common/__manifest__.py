# -*- coding: utf-8 -*-
# Part of Tele Module Developed by Tele INC.
# See LICENSE file for full copyright and licensing details.
{
    # Theme information
    'name': 'Default Theme Common',
    'category': 'Website',
    'version': '1.0.0.3',
    'author': 'Tele INC.',
    'website': 'https://www.tele.studio',
    'summary': 'Default Theme Common',
    'description': """Default Theme Common""",
    'depends': [
        'website',
        'website_blog',
        'portal',
        'theme_default',
        'web_editor',
        'website_sale',
        'website_sale_stock',
        'website_sale_wishlist',
        'website_sale_comparison',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/manifest.xml',
        'views/pwa_offline.xml',
        'views/brand_template.xml',
        'views/category_template.xml',
        #Megamenus
        'views/megamenus/megamenu_one_snippet.xml',
        # 'views/megamenus/megamenu_two_snippet.xml',
        'views/megamenus/megamenu_four_snippet.xml',
    ],

    'images': [
        'static/description/banner.jpg'
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'TPL-1',
}