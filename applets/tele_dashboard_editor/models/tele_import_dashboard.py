import base64
import logging
from tele import api, fields, models, _
from tele.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TeleDashboardEditorImport(models.TransientModel):
    _name = 'tele_dashboard_editor.import'
    _description = 'Import Dashboard'

    tele_import_dashboard = fields.Binary(string="Upload Dashboard", attachment=True)
    tele_top_menu_id = fields.Many2one('ir.ui.menu', string="Show Under Menu", domain="[('parent_id','=',False)]",
                                     required=True,
                                     default=lambda self: self.env['ir.ui.menu'].search(
                                         [('name', '=', 'My Dashboard')]))

    def tele_do_action(self):
        for rec in self:
            try:
                tele_result = base64.b64decode(rec.tele_import_dashboard)
                self.env['tele_dashboard_editor.board'].tele_import_dashboard(tele_result, self.tele_top_menu_id)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
            except Exception as E:
                _logger.warning(E)
                raise ValidationError(_(E))
