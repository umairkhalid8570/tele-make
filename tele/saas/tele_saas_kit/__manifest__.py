# -*- coding: utf-8 -*-
#################################################################################
# Author      : Tele INC. (<https://tele.studio/>)
# Copyright(c): 2021-Present Tele INC.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.tele.studio/license.html/>
#################################################################################
{
  "name"                 :  "Tele SaaS",
  "summary"              :  """Tele SaaS Kit allows you to run your Tele As A SaaS business.""",
  "category"             :  "Extra Tools",
  "version"              :  "1.2.0",
  "sequence"             :  1,
  "author"               :  "Tele INC.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.tele.studio/",
  "description"          :  """Provide Tele as a Service(Saas) on your servers with Tele saas Kit.""",
  "live_test_url"        :  "http://teledemotele.studio/demo_feedback?module=tele_saas_kit",
  "depends"              :  [
                             'sale_management',
                             'portal',
                             'base',
                             'website_sale',
                             'account',
                            ],
  "data"                 :  [
                             'security/tele_saas_kit_security.xml',
                             'security/ir.model.access.csv',
                             'views/res_config_views.xml',
                             'data/contract_sequence.xml',
                             'data/client_sequence.xml',
                             'data/email_templates.xml',
                             'data/contract_expiry_template.xml',
                             'views/subdomain_page.xml',
                             'data/recurring_invoice_cron.xml',
                             'data/client_creation_cron.xml',
                             'data/contract_expiry_cron.xml',
                             'views/saas_server_view.xml',
                             'views/module_category_view.xml',
                             'views/module_view.xml',
                             'views/product_view.xml',
                             'views/account_invoice_view.xml',
                             'wizards/contract_creation_view.xml',
                             'wizards/disable_client_wizard.xml',
                             'wizards/custom_domain_wizard_view.xml',
                             'views/custom_domain.xml',
                             'views/saas_plan_view.xml',
                             'views/saas_contract_view.xml',
                             'views/saas_client_view.xml',
                             'views/sale_view.xml',
                             'views/saas_portal_templates.xml',
                             'views/user_pricing_template.xml',
                             'views/menuitems.xml',
                            ],
  "assets"               : {
                            'web.assets_frontend': [
                              "/tele_saas_kit/static/src/js/subdomain_page.js",
                              "/tele_saas_kit/static/src/js/user_pricing_modal.js",
                              "/tele_saas_kit/static/src/js/user_pricing.js",
                              "https://fonts.googleapis.com",
                              "https://fonts.gstatic.com",
                              "https://fonts.googleapis.com/css2?family=Source+Sans+Pro:ital,wght@0,400;0,600;1,400;1,600&amp;display=swap",
                              "https://fonts.googleapis.com/css?family=Tangerine",
                              "/tele_saas_kit/static/src/css/contract_page.css"
                            ]
                           },
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  699,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['urllib']},
}
