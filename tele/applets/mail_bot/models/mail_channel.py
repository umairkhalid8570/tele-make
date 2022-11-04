# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

from tele import api, models, _


class Channel(models.Model):
    _inherit = 'mail.channel'

    def execute_command_help(self, **kwargs):
        super().execute_command_help(**kwargs)
        self.env['mail.bot']._apply_logic(self, kwargs, command="help")  # kwargs are not usefull but...

    @api.model
    def init_telebot(self):
        if self.env.user.telebot_state in [False, 'not_initialized']:
            telebot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
            channel_info = self.channel_get([telebot_id])
            channel = self.browse(channel_info['id'])
            message = _("Hello,<br/>Tele's chat helps employees collaborate efficiently. I'm here to help you discover its features.<br/><b>Try to send me an emoji</b> <span class=\"o_telebot_command\">:)</span>")
            channel.sudo().message_post(body=message, author_id=telebot_id, message_type="comment", subtype_xmlid="mail.mt_comment")
            self.env.user.telebot_state = 'onboarding_emoji'
            return channel
