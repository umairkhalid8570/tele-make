# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

import tele
import tele.tests


@tele.tests.common.tagged('post_install', '-at_install')
class TestSnippets(tele.tests.HttpCase):

    def test_01_newsletter_popup(self):
        self.start_tour("/?enable_editor=1", "newsletter_popup_edition", login='admin')
        self.start_tour("/", "newsletter_popup_use", login=None)
        mailing_list = self.env['mailing.list'].search([], limit=1)
        emails = mailing_list.contact_ids.mapped('email')
        self.assertIn("hello@world.com", emails)

    def test_02_newsletter_block_edition(self):
        self.start_tour("/?enable_editor=1", "newsletter_block_edition", login='admin')
