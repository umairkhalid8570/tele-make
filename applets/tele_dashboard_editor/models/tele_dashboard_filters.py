from tele import models, fields, api, _
from tele.exceptions import ValidationError
from tele.tools.safe_eval import safe_eval


class TeleDashboardEditorTemplate(models.Model):
    _name = 'tele_dashboard_editor.board_defined_filters'
    _description = 'Dashboard Editor Defined Filters'

    name = fields.Char("Filter Label")
    tele_dashboard_board_id = fields.Many2one('tele_dashboard_editor.board', string="Dashboard")
    tele_model_id = fields.Many2one('ir.model', string='Model',
                                  domain="[('access_ids','!=',False),('transient','=',False),"
                                         "('model','not ilike','base_import%'),('model','not ilike','ir.%'),"
                                         "('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),"
                                         "('model','!=','mail.thread'),('model','not ilike','tele_dash%'), ('model','not ilike','tele_to%')]",
                                  help="Data source to fetch and read the data for the creation of dashboard items. ")
    tele_domain = fields.Char(string="Domain", help="Define conditions for filter. ")
    tele_domain_temp = fields.Char(string="Domain Substitute")
    tele_model_name = fields.Char(related='tele_model_id.model', string="Model Name")
    display_type = fields.Selection([
        ('line_section', "Section")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(default=10,
                              help="Gives the sequence order when displaying a list of payment terms lines.")
    tele_is_active = fields.Boolean(string="Active")

    @api.onchange('tele_domain')
    def tele_domain_onchange(self):
        for rec in self:
            if rec.tele_model_id:
                try:
                    tele_domain = rec.tele_domain
                    if tele_domain and "%UID" in tele_domain:
                        tele_domain = tele_domain.replace('"%UID"', str(self.env.user.id))
                    if tele_domain and "%MYCOMPANY" in tele_domain:
                        tele_domain = tele_domain.replace('"%MYCOMPANY"', str(self.env.company.id))
                    self.env[rec.tele_model_id.model].search_count(safe_eval(tele_domain))
                except Exception as e:
                    raise ValidationError(_("Something went wrong . Possibly it is due to wrong input type for domain"))

    @api.constrains('tele_domain', 'tele_model_id')
    def tele_domain_check(self):
        for rec in self:
            if rec.tele_model_id and not rec.tele_domain:
                raise ValidationError(_("Domain can not be empty"))



class TeleDashboardEditorTemplate(models.Model):
    _name = 'tele_dashboard_editor.board_custom_filters'
    _description = 'Dashboard Editor Custom Filters'

    name = fields.Char("Filter Label")
    tele_dashboard_board_id = fields.Many2one('tele_dashboard_editor.board', string="Dashboard")
    tele_model_id = fields.Many2one('ir.model', string='Model',
                                  domain="[('access_ids','!=',False),('transient','=',False),"
                                         "('model','not ilike','base_import%'),('model','not ilike','ir.%'),"
                                         "('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),"
                                         "('model','!=','mail.thread'),('model','not ilike','tele_dash%'), ('model','not ilike','tele_to%')]",
                                  help="Data source to fetch and read the data for the creation of dashboard items. ")
    tele_domain_field_id = fields.Many2one('ir.model.fields',
                                         domain="[('model_id','=',tele_model_id),"
                                                "('name','!=','id'),('store','=',True),"
                                                "('ttype', 'in', ['boolean', 'char', "
                                                "'date', 'datetime', 'float', 'integer', 'html', 'many2many', "
                                                "'many2one', 'monetary', 'one2many', 'text', 'selection'])]",
                                         string="Domain Field")
