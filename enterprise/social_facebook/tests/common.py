# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.


from unittest.mock import patch

from tele.applets.social_facebook.models.social_account import SocialAccountFacebook
from tele.applets.social.tests.common import SocialCase


class SocialFacebookCommon(SocialCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(SocialAccountFacebook, '_compute_statistics', lambda x: None), \
             patch.object(SocialAccountFacebook, '_create_default_stream_facebook', lambda *args, **kwargs: None):
            super(SocialFacebookCommon, cls).setUpClass()
