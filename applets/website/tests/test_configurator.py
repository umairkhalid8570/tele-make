# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

import tele.tests
from tele.applets.iap.tools.iap_tools import iap_jsonrpc_mocked
from tele.tools import mute_logger

class TestConfiguratorCommon(tele.tests.HttpCase):

    def _theme_upgrade_upstream(self):
        # patch to prevent module install/upgrade during tests
        pass

    def setUp(self):
        super().setUp()

        def iap_jsonrpc_mocked_configurator(*args, **kwargs):
            endpoint = args[0]
            params = kwargs.get('params', {})
            language = params.get('lang', 'en_US')
            if endpoint.endswith('/api/website/1/configurator/industries'):
                if language == 'fr_FR':
                    return {"industries": [
                        {"id": 1, "label": "abbey in fr"},
                        {"id": 2, "label": "aboriginal and torres strait islander organisation in fr"},
                        {"id": 3, "label": "aboriginal art gallery in fr"},
                        {"id": 4, "label": "abortion clinic in fr"},
                        {"id": 5, "label": "abrasives supplier in fr"},
                        {"id": 6, "label": "abundant life church in fr"}]}
                else:
                    return {"industries": [
                        {"id": 1, "label": "abbey"},
                        {"id": 2, "label": "aboriginal and torres strait islander organisation"},
                        {"id": 3, "label": "aboriginal art gallery"},
                        {"id": 4, "label": "abortion clinic"},
                        {"id": 5, "label": "abrasives supplier"},
                        {"id": 6, "label": "abundant life church"}]}
            elif '/api/website/2/configurator/recommended_themes' in endpoint:
                return []
            elif '/api/website/2/configurator/custom_resources/' in endpoint:
                return {'images': {}}

            iap_jsonrpc_mocked()

        iap_patch = patch('tele.applets.iap.tools.iap_tools.iap_jsonrpc', iap_jsonrpc_mocked_configurator)
        iap_patch.start()
        self.addCleanup(iap_patch.stop)

        patcher = patch('tele.applets.website.models.ir_module_module.IrModuleModule._theme_upgrade_upstream', wraps=self._theme_upgrade_upstream)
        patcher.start()
        self.addCleanup(patcher.stop)

@tele.tests.common.tagged('post_install', '-at_install')
class TestConfiguratorTranslation(TestConfiguratorCommon):

    def test_01_configurator_translation(self):
        with mute_logger('tele.applets.base.models.ir_translation'):
            self.env["base.language.install"].create({'lang': 'fr_FR', 'overwrite': True}).lang_install()
        website_fr = self.env['website'].create({
            'name': "Website Fr",
            'default_lang_id': self.env.ref('base.lang_fr').id
        })
        # disable configurator todo to ensure this test goes through
        active_todo = self.env['ir.actions.todo'].search([('state', '=', 'open')], limit=1)
        active_todo.update({'state': 'done'})
        self.start_tour('/website/force/%s?path=%%2Fwebsite%%2Fconfigurator' % website_fr.id, 'configurator_translation', login='admin')
