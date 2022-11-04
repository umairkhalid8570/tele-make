# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import models


class Users(models.Model):
    _inherit = 'res.users'

    def get_totp_invite_url(self):
        if not self.has_group('base.group_user'):
            return '/my/security'
        else:
            return super(Users, self).get_totp_invite_url()
