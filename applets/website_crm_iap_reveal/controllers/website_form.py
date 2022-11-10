# -*- coding: utf-8 -*-
import json

from tele import http
from tele.applets.website.controllers.form import WebsiteForm
from tele.http import request


class ContactController(WebsiteForm):

    def _handle_website_form(self, model_name, **kwargs):
        if model_name == 'crm.lead':
            # Add the ip_address to the request in order to add this to the lead
            # that will be created. With this, we avoid to create a lead from
            # reveal if a lead is already created from the contact form.
            request.params['reveal_ip'] = request.httprequest.remote_addr

        return super(ContactController, self)._handle_website_form(model_name, **kwargs)
