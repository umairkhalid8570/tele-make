# -*- coding: utf-8 -*-
# Part of Tele. See LICENSE file for full copyright and licensing details.

import tele.modules.db
from . import models
from tele import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

def post_init(cr, registry):
    # if not registry.has_unaccent: # FIXME: tele/tele#347
    if not tele.modules.db.has_unaccent(cr):
        _logger.warning('pg extension "unaccent" not loaded, deduplication rules of type "accent" will be treated as "exaxt"')

def uninstall_hook(cr, registry):
    """ This method will remove all the server actions used for 'Merge Action' in the contextual menu. """
    env = api.Environment(cr, SUPERUSER_ID, {})
    models_to_clean = env['ir.model'].search([('ref_merge_ir_act_server_id', '!=', False)])
    actions_to_remove = models_to_clean.mapped('ref_merge_ir_act_server_id')
    actions_to_remove.unlink()
