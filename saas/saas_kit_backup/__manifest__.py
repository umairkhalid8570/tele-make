# -*- coding: utf-8 -*-
#################################################################################
# Author      : Tele INC. (<https://tele.studio/>)
# Copyright(c): 2022-Present Tele INC.
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
  "name"                 :  "Saas Kit Backup",
  "summary"              :  """Module provide feature to saas clients to take backups of client instance's database and later download them.""",
  "category"             :  "Extra Tools",
  "version"              :  "1.0.4",
  "author"               :  "Tele INC.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.tele.studio/",
  "description"          :  """Module provide feature to saas clients to take backups of client instance's database and later download them.""",
  "live_test_url"        :  "http://teledemo.tele.studio/demo_feedback?module=saas_kit_backup",
  "depends"              :  [
                             'tele_saas_kit',
                             'tele_backup_restore',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'wizard/backup_process_wizard.xml',
                             'views/saas_client_view.xml',
                             'views/saas_server_view.xml',
                             'views/backup_process.xml',
                             'views/backup_template.xml',
                             'views/contract_portal_page.xml',
                            ],
  "assets"               : {
                              'web.assets_frontend': [
                                '/saas_kit_backup/static/src/js/backup_process.js',
                                '/saas_kit_backup/static/src/css/backup_process.css'
                              ]
                            },
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
