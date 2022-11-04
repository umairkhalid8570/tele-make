# -*- coding: utf-8 -*-

from tele import api, fields, models
from tele.applets.http_routing.models.ir_http import slug
from tele.tools.translate import html_translate


class WebsiteResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'website.seo.metadata']

    website_description = fields.Html('Website Partner Full Description', strip_style=True, translate=html_translate)
    website_short_description = fields.Text('Website Partner Short Description', translate=True)

    def _compute_website_url(self):
        super(WebsiteResPartner, self)._compute_website_url()
        for partner in self:
            partner.website_url = "/partners/%s" % slug(partner)
