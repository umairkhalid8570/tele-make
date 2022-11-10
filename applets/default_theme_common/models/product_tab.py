# -*- coding: utf-8 -*-
# Part of Tele Module Developed by Tele INC.
# See LICENSE file for full copyright and licensing details.

from tele import models, fields, api
from tele import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tab_ids = fields.Many2many('product.tab','product_tab_table','tab_ids','product_ids',string="Tab")
    product_label_id = fields.Many2one('product.label.tele',string="Product Label")
    service_ids = fields.Many2many("product.service",string="Website Services")
    highlights_ids = fields.Many2many("product.highlights",string="Website Highlights")
    hover_image = fields.Image(string="Product Hover Image")
    tag_ids = fields.Many2many("product.tag",string="Tag")

class ProductTag(models.Model):
    _name = "product.tag"
    _description = "Product Tag"


    name = fields.Char("Name")
    sequence = fields.Integer("Sequence")
    
class ProductTab(models.Model):
    _name = 'product.tab'
    _description = 'Product Tab'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
    content = fields.Html(string="Content")
    product_ids = fields.Many2many('product.template','product_tab_table','product_ids','tab_ids', string="product")

class ProductLabelBizople (models.Model):
     _name = 'product.label.tele'
     _description = 'Product Label'
     
     _SELECTION_STYLE = [
        ('rounded', 'Rounded'),
        ('outlinesquare', 'Outline Square'),
        ('outlineround', 'Outline Rounded'),
        ('flat', 'Flat'),
    ]
     
     name = fields.Char(string="Name", translate=True, required=True)
     label_bg_color = fields.Char(string="Label Background Color", required=True,default="#f6513b")
     label_font_color = fields.Char(string="Label Font Color", required=True, default="#ffffff")
     label_style = fields.Selection(
        string='Label Style', selection=_SELECTION_STYLE, default='rounded')