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
  "name"                 :  "Tele SaaS Custom Plans",
  "summary"              :  """Tele SaaS Custom Plans allows you to provide option to your clients to select custom Plans of their choice for Tele Saas Kit""",
  "category"             :  "Extra Tools",
  "version"              :  "1.0.7",
  "sequence"             :  1,
  "author"               :  "Tele INC.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.tele.studio/",
  "description"          :  """Provide Custom plan option for Tele saas Kit.""",
  "live_test_url"        :  "http://teledemotele.studio/demo_feedback?module=saas_kit_custom_plans",
  "depends"              :  [
                             'tele_saas_kit',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/saas_client.xml',
                             'views/product_view.xml',
                             'views/product_page.xml',
                             'views/saas_module.xml',
                             'views/tele_version_view.xml',
                             'views/res_config_view.xml',
                             'data/request_sequence.xml',
                             'data/contract_expiry_warning_template.xml',
                             'views/contract_view.xml',
                             'views/menuitems.xml',
                             'views/page_template.xml',
                             'views/portal_template.xml',
                             'data/product.xml',
                             'data/module_installation_crone.xml',
                             'data/contract_expiry_warning_mail_crone.xml'
                            ],
  "assets"               : {
                            "web.assets_frontend": [
                              '/saas_kit_custom_plans/static/src/js/custom_plan.js',
                              '/saas_kit_custom_plans/static/src/js/update_app.js',
                              '/saas_kit_custom_plans/static/src/css/custom_plan_apps_page.css',
                            ]
                           },
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
