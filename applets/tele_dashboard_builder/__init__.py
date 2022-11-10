# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import common_lib
from . import wizard

from tele.api import Environment, SUPERUSER_ID


def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    for rec in env['tele_dashboard_builder.board'].search([]):
        rec.tele_dashboard_client_action_id.unlink()
        rec.tele_dashboard_menu_id.unlink()
