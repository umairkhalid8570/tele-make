# Part of Tele. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-

import tele.tests


@tele.tests.tagged('post_install', '-at_install')
class TestUi(tele.tests.HttpCase):

    def test_new_app_and_report(self):
        self.start_tour("/web", 'tele_studio_new_app_tour', login="admin")

        # the report tour is based on the result of the former tour
        self.start_tour("/web?debug=tests", 'tele_studio_new_report_tour', login="admin")
        self.start_tour("/web?debug=tests", "tele_studio_new_report_basic_layout_tour", login="admin")

    def test_optional_fields(self):
        self.start_tour("/web?debug=tests", 'tele_studio_hide_fields_tour', login="admin")

    def test_model_option_value(self):
        self.start_tour("/web?debug=tests", 'tele_studio_model_option_value_tour', login="admin")

    def test_rename(self):
        self.start_tour("/web?debug=tests", 'tele_studio_tests_tour', login="admin", timeout=200)

    def test_approval(self):
        self.start_tour("/web?debug=tests", 'tele_studio_approval_tour', login="admin")

    def test_background(self):
        attachment = self.env['ir.attachment'].create({
            'datas': b'R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=',
            'name': 'testFilename.gif',
            'public': True,
            'mimetype': 'image/gif'
        })
        self.env.company.background_image = attachment.datas
        self.start_tour("/web?debug=tests", 'tele_studio_custom_background_tour', login="admin")
