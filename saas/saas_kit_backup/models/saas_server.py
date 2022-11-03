# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Tele INC. (<https://tele.studio/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.tele.studio/license.html/>
#################################################################################

from tele import models, fields, tools
from tele.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)


LOCATION = [
    ('local', 'Local'),
]


class SaasServerBackup(models.Model):
    _inherit = 'saas.server'
    
    
    backup_location = fields.Selection(selection=LOCATION, string="Backup Location", default='local')
    retention = fields.Integer(string="Backup Retention")
