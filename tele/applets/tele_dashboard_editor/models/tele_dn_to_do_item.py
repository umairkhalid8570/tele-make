import json
from tele import models, fields, api, _
import copy
import re
from tele.exceptions import ValidationError, UserError

class TeleDashboardEditorItems(models.Model):
    _inherit = 'tele_dashboard_editor.item'

    tele_to_do_preview = fields.Char("To Do Preview", default="To Do Preview")
    tele_dn_header_lines = fields.One2many('tele_to.do.headers', 'tele_dn_item_id')
    tele_to_do_data = fields.Char(string="To Do Data in JSon", compute='tele_get_to_do_view_data', compute_sudo=False)
    tele_header_bg_color = fields.Char(string="Header Background Color", default="#8e24aa,0.99",
                                     help=' Select the background color with transparency. ')

    @api.depends('tele_dn_header_lines', 'tele_dashboard_item_type')
    def tele_get_to_do_view_data(self):
        for rec in self:
            tele_to_do_data = rec._teleGetToDOData()
            rec.tele_to_do_data = tele_to_do_data

    def _teleGetToDOData(self):
        tele_to_do_data = {
            'label': [],
            'tele_link': [],
            'tele_href_id': [],
            'tele_section_id': [],
            'tele_content': {},
            'tele_content_record_id': {},
            'tele_content_active': {}
        }

        if self.tele_dn_header_lines:
            for tele_dn_header_line in self.tele_dn_header_lines:
                tele_to_do_header_label = tele_dn_header_line.tele_to_do_header[:]
                tele_to_do_data['label'].append(tele_to_do_header_label)
                tele_dn_header_line_id = str(tele_dn_header_line.id)
                if type(tele_dn_header_line.id).__name__ != 'int' and tele_dn_header_line.id.ref != None:
                    tele_dn_header_line_id = tele_dn_header_line.id.ref
                if ' ' in  tele_dn_header_line.tele_to_do_header:
                    tele_temp = tele_dn_header_line.tele_to_do_header.replace(" ", "")
                    tele_to_do_data['tele_link'].append('#' + tele_temp + tele_dn_header_line_id)
                    tele_to_do_data['tele_href_id'].append(tele_temp + str(tele_dn_header_line.id))

                elif tele_dn_header_line.tele_to_do_header[0].isdigit():
                    tele_temp = tele_dn_header_line.tele_to_do_header.replace(
                        tele_dn_header_line.tele_to_do_header[0], 'z')
                    tele_to_do_data['tele_link'].append('#' + tele_temp + tele_dn_header_line_id)
                    tele_to_do_data['tele_href_id'].append(tele_temp + str(tele_dn_header_line.id))
                else:
                    tele_to_do_data['tele_link'].append('#' + tele_dn_header_line.tele_to_do_header + tele_dn_header_line_id)
                    tele_to_do_data['tele_href_id'].append(tele_dn_header_line.tele_to_do_header + str(tele_dn_header_line.id))
                tele_to_do_data['tele_section_id'].append(str(tele_dn_header_line.id))
                if len(tele_dn_header_line.tele_to_do_description_lines):
                    for tele_to_do_description_line in tele_dn_header_line.tele_to_do_description_lines:
                        if ' ' in tele_dn_header_line.tele_to_do_header or tele_dn_header_line.tele_to_do_header[0].isdigit():
                            if tele_to_do_data['tele_content'].get(tele_temp +
                                                               str(tele_dn_header_line.id), False):

                                tele_to_do_data['tele_content'][tele_temp +
                                                            str(tele_dn_header_line.id)].append(
                                    tele_to_do_description_line.tele_description)
                                tele_to_do_data['tele_content_record_id'][tele_temp +
                                                                      str(tele_dn_header_line.id)].append(
                                    str(tele_to_do_description_line.id))
                                tele_to_do_data['tele_content_active'][tele_temp +
                                                                   str(tele_dn_header_line.id)].append(
                                    str(tele_to_do_description_line.tele_active))
                            else:
                                tele_to_do_data['tele_content'][tele_temp +
                                                            str(tele_dn_header_line.id)] = [
                                    tele_to_do_description_line.tele_description]
                                tele_to_do_data['tele_content_record_id'][tele_temp +
                                                                      str(tele_dn_header_line.id)] = [
                                    str(tele_to_do_description_line.id)]
                                tele_to_do_data['tele_content_active'][tele_temp +
                                                                   str(tele_dn_header_line.id)] = [
                                    str(tele_to_do_description_line.tele_active)]
                        else:
                            if tele_to_do_data['tele_content'].get(tele_dn_header_line.tele_to_do_header +
                                                               str(tele_dn_header_line.id), False):

                                tele_to_do_data['tele_content'][tele_dn_header_line.tele_to_do_header +
                                                            str(tele_dn_header_line.id)].append(
                                    tele_to_do_description_line.tele_description)
                                tele_to_do_data['tele_content_record_id'][tele_dn_header_line.tele_to_do_header +
                                                                      str(tele_dn_header_line.id)].append(
                                    str(tele_to_do_description_line.id))
                                tele_to_do_data['tele_content_active'][tele_dn_header_line.tele_to_do_header +
                                                                   str(tele_dn_header_line.id)].append(
                                    str(tele_to_do_description_line.tele_active))
                            else:
                                tele_to_do_data['tele_content'][tele_dn_header_line.tele_to_do_header +
                                                            str(tele_dn_header_line.id)] = [
                                    tele_to_do_description_line.tele_description]
                                tele_to_do_data['tele_content_record_id'][tele_dn_header_line.tele_to_do_header +
                                                                      str(tele_dn_header_line.id)] = [
                                    str(tele_to_do_description_line.id)]
                                tele_to_do_data['tele_content_active'][tele_dn_header_line.tele_to_do_header +
                                                                   str(tele_dn_header_line.id)] = [
                                    str(tele_to_do_description_line.tele_active)]

            tele_to_do_data = json.dumps(tele_to_do_data)
        else:
            tele_to_do_data = False
        return tele_to_do_data




class TeleToDoheaders(models.Model):
    _name = 'tele_to.do.headers'
    _description = "to do headers"

    tele_dn_item_id = fields.Many2one('tele_dashboard_editor.item')
    tele_to_do_header = fields.Char('Header')
    tele_to_do_description_lines = fields.One2many('tele_to.do.description', 'tele_to_do_header_id')

    @api.constrains('tele_to_do_header')
    def tele_to_do_header_check(self):
        for rec in self:
            if rec.tele_to_do_header:
                tele_check = bool(re.match('^[A-Z, a-z,0-9,_]+$', rec.tele_to_do_header))
                if not tele_check:
                    raise ValidationError(_("Special characters are not allowed only string and digits allow for section header"))

    @api.onchange('tele_to_do_header')
    def tele_to_do_header_onchange(self):
        for rec in self:
            if rec.tele_to_do_header:
                tele_check = bool(re.match('^[A-Z, a-z,0-9,_]+$', rec.tele_to_do_header))
                if not tele_check:
                    raise ValidationError(_("Special characters are not allowed only string and digits allow for section header"))

class TeleToDODescription(models.Model):
    _name = 'tele_to.do.description'
    _description = 'to do description'

    tele_to_do_header_id = fields.Many2one('tele_to.do.headers')
    tele_description = fields.Text('Description')
    tele_active = fields.Boolean('Active Description', default=True)
