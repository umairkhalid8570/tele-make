# Part of Tele. See LICENSE file for full copyright and licensing details.

from . import models
from . import controllers

from tele.applets.payment import reset_payment_acquirer


def uninstall_hook(cr, registry):
    reset_payment_acquirer(cr, registry, 'sips')
