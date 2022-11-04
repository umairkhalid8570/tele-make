# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'documents.mixin']

    def _get_document_tags(self):
        company = self.company_id or self.env.company
        return company.product_tags

    def _get_document_folder(self):
        company = self.company_id or self.env.company
        return company.product_folder

    def _check_create_documents(self):
        company = self.company_id or self.env.company
        return company.documents_product_settings and super()._check_create_documents()
