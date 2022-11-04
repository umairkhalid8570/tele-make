# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models


class HrJob(models.Model):
    _name = 'hr.job'
    _inherit = ['hr.job', 'documents.mixin']

    def _get_document_folder(self):
        return self.company_id.recruitment_folder_id

    def _check_create_documents(self):
        return self.company_id.documents_recruitment_settings and super()._check_create_documents()
