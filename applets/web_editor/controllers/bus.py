# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

import re

from tele.http import request
from tele.applets.bus.controllers.main import BusController
from tele.exceptions import AccessDenied


class EditorCollaborationController(BusController):
    # ---------------------------
    # Extends BUS Controller Poll
    # ---------------------------
    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            # Do not alter original list.
            channels = list(channels)
            for channel in channels:
                if isinstance(channel, str):
                    match = re.match(r'editor_collaboration:(\w+(?:\.\w+)*):(\w+):(\d+)', channel)
                    if match:
                        model_name = match[1]
                        field_name = match[2]
                        res_id = int(match[3])

                        # Verify access to the edition channel.
                        if not request.env.user.has_group('base.group_user'):
                            raise AccessDenied()

                        document = request.env[model_name].browse([res_id])

                        document.check_access_rights('read')
                        document.check_field_access_rights('read', [field_name])
                        document.check_access_rule('read')
                        document.check_access_rights('write')
                        document.check_field_access_rights('write', [field_name])
                        document.check_access_rule('write')

                        channels.append((request.db, 'editor_collaboration', model_name, field_name, res_id))
        return super(EditorCollaborationController, self)._poll(dbname, channels, last, options)
