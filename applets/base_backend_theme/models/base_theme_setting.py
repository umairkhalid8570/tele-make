# -*- coding: utf-8 -*-

from attr import field
from tele import api, fields, models, tools

DEFAULT_PRIMARY = '#000000'
DEFAULT_SECONDARY = '#000000'

#SOLID theme variable
SOLID_COLOR_1 = '#07a650'
SOLID_COLOR_2 = '#e6f3ec'
SOLID_COLOR_3 = '#f5f5fa'
SOLID_BUTTON_COLOR_1 = '#07a650'
SOLID_BUTTON_COLOR_2 = '#e6f3ec'
SOLID_BUTTON_COLOR_3 = '#eeeeee'
SOLID_SIDEBAR_STYLE_1 = 'default'
SOLID_SIDEBAR_POSITIN_1 = 'left'
SOLID_FONT_STYLE_1 = 'publicsans'
SOLID_CHECKBOX_STYLE_1 = 'style_1'
SOLID_RADIO_BTN_STYLE_1 = 'style_2'

#GRADIENT theme variable
GRADIENT_COLOR_1 = '#4f46e5'
GRADIENT_COLOR_2 = '#e2e8f0'
GRADIENT_COLOR_3 = '#f1f5f9'
GRADIENT_BUTTON_COLOR_1 = '#4f46e5'
GRADIENT_BUTTON_COLOR_2 = '#e2e8f0'
GRADIENT_BUTTON_COLOR_3 = '#f1f5f9'
GRADIENT_SIDEBAR_STYLE_1 = 'drawer'
GRADIENT_SIDEBAR_POSITIN_1 = 'left'
GRADIENT_FONT_STYLE_1 = 'default'
GRADIENT_FONT_STYLE_1 = 'publicsans'
GRADIENT_CHECKBOX_STYLE_1 = 'style_1'
GRADIENT_RADIO_BTN_STYLE_1 = 'style_2'

#Dark theme variable
DARK_COLOR_1 = '#6BB6C9'
DARK_COLOR_2 = '#ffffff'
DARK_COLOR_3 = '#1D6E93'
DARK_BUTTON_COLOR_1 = '#6BB6C9'
DARK_BUTTON_COLOR_2 = '#ffffff'
DARK_BUTTON_COLOR_3 = '#1D6E93'
DARK_SIDEBAR_STYLE_1 = 'hovertoshow'
DARK_SIDEBAR_POSITIN_1 = 'left'
DARK_FONT_STYLE_1 = 'default'
DARK_FONT_STYLE_1 = 'publicsans'
DARK_CHECKBOX_STYLE_1 = 'style_1'
DARK_RADIO_BTN_STYLE_1 = 'style_2'



import base64
URL = '/base_backend_theme/static/src/scss/base_theme_variables.scss'
class RtAlphaThemeSettings(models.Model):
    """
    
    Customise the alpha backend theme
    
    """

    _name = 'base.theme.settings'
    _description = 'Base Theme Settings'


    name = fields.Char(string="Name", required = True)
    
    theme_color_type = fields.Selection([ 
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),       
        ],string="Theme Color Type", default="style_1")  

    theme_primary_1_color = fields.Char(string="Color 1")
    theme_primary_2_color = fields.Char(string="Color 2")
    theme_secondary_color = fields.Char(string="Secondary Color")
  
    
    theme_background_type = fields.Selection([
        ("none",'None'),
        # ("color",'Color'),
        ("image",'Image'),        
        ],string="Background Type", default="none")
    theme_background_color = fields.Char(string="Theme Background Color")
    theme_background_image = fields.Image(string="Theme Background Image")
    
    button_type = fields.Selection([
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),        
        ],string="Button Type", default="style_1")  
    
    button_color_type = fields.Selection([
        ("solid",'Solid'),
        ("gradient",'Gradient'),        
        ],string="Button Color Type", default="solid")  

    button_primary_1_color = fields.Char(string="Button Primary 1 Color")
    button_primary_2_color = fields.Char(string="Button Primary 2 Color")
    button_secondary_color = fields.Char(string="Secondary Button Color")
  
  
    is_use_google_font = fields.Boolean(string="Use Google Font?")
    google_font_family = fields.Char(string="Google font-family")
    
    theme_gradient_preview = fields.Html(compute='_theme_gradient_preview',
                          sanitize=False,
                          sanitize_tags=False,
                          sanitize_attributes=False,
                          sanitize_style=False,
                          sanitize_form=False,
                          strip_style=False,
                          strip_classes=False)  
  
  
    button_gradient_preview = fields.Html(compute='_button_gradient_preview',
                          sanitize=False,
                          sanitize_tags=False,
                          sanitize_attributes=False,
                          sanitize_style=False,
                          sanitize_form=False,
                          strip_style=False,
                          strip_classes=False)  
    sidebar_style = fields.Selection([
        ("default",'Default'),
        ("drawer",'Drawer'),
        ("hovertoshow",'Hover to Show'),        
        ],string="Sidebar Style", default="default")   
    sidebar_position = fields.Selection([
        ("left",'Left'),
        ("bottom",'Bottom'),    
        ],string="Sidebar Position", default="left") 
    font_style = fields.Selection([
        ("default",'Default'),
        ("inter",'Inter'),
        ("roboto",'Roboto'), 
        ("poppins",'Poppins'), 
        ("publicsans",'Public Sans'),
        ("raleway",'Raleway'),
        ("rubik",'Rubik'), 
        ("lora",'Lora'),        
        ],string="Font Style", default="default")   
    checkbox_style = fields.Selection([
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),
        ("style_4",'Style 4'),        
        ],string="Checkbox Style", default="style_1")
    radio_btn_style = fields.Selection([
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),
        ("style_4",'Style 4'),        
        ],string="Radio Button Style", default="style_1")      
    theme_loading_type = fields.Selection([
        ("default",'default'),
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),
        ("image",'Gif'),        
        ],string="Loading Type", default="default")     
    theme_loading_image = fields.Image(string="Loading Gif")
    theme_scrollbar_style = fields.Selection([
        ("default",'default'),
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),
        ("style_4",'Style 4'),        
        ],string="Scrollbar Style", default="style_1")  
    theme_tab_style = fields.Selection([
        ("default",'default'),
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),
        ("style_4",'Style 4'),
        ("style_5",'Style 5'),        
        ],string="Tab Style", default="default")     
    theme_form_style = fields.Selection([
        ("default",'default'),
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),
        ("style_4",'Style 4'),
        ("style_5",'Style 5'),        
        ],string="Tab Style", default="default") 
    theme_separator_style = fields.Selection([
        ("default",'default'),
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),
        ("style_4",'Style 4'),
        ("style_5",'Style 5'),        
        ],string="Tab Style", default="default") 
    theme_popup_style = fields.Selection([
        ("default",'default'),
        ("style_1",'Style 1'),
        ("style_2",'Style 2'),
        ("style_3",'Style 3'),
        ("style_4",'Style 4'),
        ("style_5",'Style 5'),        
        ],string="Tab Style", default="default")        
    base_sticky_tree_view = fields.Boolean(string="Sticky Tree View")
    base_one2many_field_tree_view = fields.Boolean(string="One2many Field Tree View")
    base_sticky_form_view_chatter = fields.Boolean(string="Sticky Form View Chatter")
    base_sticky_form_view_statusbar = fields.Boolean(string="Sticky Form View Statusbar")
    # base_sticky_pivot_view = fields.Boolean(string="Sticky Pivot View Statusbar")
    theme_font_size = fields.Selection([
        ("small",'Small'),
        ("medium",'Medium'),
        ("large",'Large'),     
        ],string="Font Size", default="medium")   


    @api.onchange('theme_color_type')
    def get_selection(self):
        if self.theme_color_type == "style_1" :
            self.theme_primary_1_color = SOLID_COLOR_1
            self.theme_primary_2_color = SOLID_COLOR_2
            self.theme_secondary_color = SOLID_COLOR_3
            self.button_type = 'style_1'
            # self.button_color_type = 'solid'
            self.button_primary_1_color = SOLID_BUTTON_COLOR_1
            self.button_primary_2_color = SOLID_BUTTON_COLOR_2
            self.button_secondary_color = SOLID_BUTTON_COLOR_3

            self.sidebar_style = SOLID_SIDEBAR_STYLE_1
            self.sidebar_position = SOLID_SIDEBAR_POSITIN_1
            self.font_style = SOLID_FONT_STYLE_1
            self.checkbox_style = SOLID_CHECKBOX_STYLE_1 
            self.radio_btn_style = SOLID_RADIO_BTN_STYLE_1 
        if self.theme_color_type == "style_2" :
            self.theme_primary_1_color = GRADIENT_COLOR_1
            self.theme_primary_2_color = GRADIENT_COLOR_2
            self.theme_secondary_color = GRADIENT_COLOR_3
            self.button_type = 'style_2'
            # self.button_color_type = 'gradient'
            self.button_primary_1_color = GRADIENT_BUTTON_COLOR_1
            self.button_primary_2_color = GRADIENT_BUTTON_COLOR_2
            self.button_secondary_color = GRADIENT_BUTTON_COLOR_3   

            self.sidebar_style = GRADIENT_SIDEBAR_STYLE_1
            self.sidebar_position = GRADIENT_SIDEBAR_POSITIN_1
            self.font_style = GRADIENT_FONT_STYLE_1
            self.checkbox_style = GRADIENT_CHECKBOX_STYLE_1 
            self.radio_btn_style = GRADIENT_RADIO_BTN_STYLE_1 
        if self.theme_color_type == "style_3" :
            self.theme_primary_1_color = DARK_COLOR_1
            self.theme_primary_2_color = DARK_COLOR_2
            self.theme_secondary_color = DARK_COLOR_3
            self.button_type = 'style_3'
            # self.button_color_type = 'solid'
            self.button_primary_1_color = DARK_BUTTON_COLOR_1
            self.button_primary_2_color = DARK_BUTTON_COLOR_2
            self.button_secondary_color = DARK_BUTTON_COLOR_3

            self.sidebar_style = DARK_SIDEBAR_STYLE_1
            self.sidebar_position = DARK_SIDEBAR_POSITIN_1
            self.font_style = DARK_FONT_STYLE_1
            self.checkbox_style = DARK_CHECKBOX_STYLE_1 
            self.radio_btn_style = DARK_RADIO_BTN_STYLE_1 
            

    @api.depends('theme_primary_1_color', 'theme_primary_2_color')
    def _theme_gradient_preview(self):
        for wizard in self:
            wizard.theme_gradient_preview = '''
            <div style="background-image: linear-gradient(to right, %s, %s);height:10px;"/>
            ''' % (self.theme_primary_1_color, self.theme_primary_2_color)
            
            
    @api.depends('button_primary_1_color', 'button_primary_2_color')
    def _button_gradient_preview(self):
        for wizard in self:
            wizard.button_gradient_preview = '''
            <div style="background-image: linear-gradient(to right, %s, %s);height:10px;"/>
            ''' % (self.button_primary_1_color, self.button_primary_2_color)
                             
  
    def action_apply_theme_settings(self):
        self.ensure_one()
        if self:
            content = """
            $base_theme_color_type:%(base_theme_color_type)s;
            $base_theme_primary_1_color:%(base_theme_primary_1_color)s;
            $base_theme_primary_2_color:%(base_theme_primary_2_color)s; 
            $base_theme_secondary_color:%(base_theme_secondary_color)s;                                  
            $base_theme_background_type:%(base_theme_background_type)s;              
            $base_button_type:%(base_button_type)s; 
            $base_button_primary_1_color:%(base_button_primary_1_color)s; 
            $base_button_primary_2_color:%(base_button_primary_2_color)s; 
            $base_button_secondary_color:%(base_button_secondary_color)s;   
            $base_sidebr_type:%(base_sidebr_type)s;
            $base_sidebar_position:%(base_sidebar_position)s;
            $base_font_style:%(base_font_style)s;
            $base_checkbox_style:%(base_checkbox_style)s;
            $base_radion_btn_style:%(base_radion_btn_style)s;
            $base_theme_loading_type:%(base_theme_loading_type)s;
            $base_theme_scrollbar_style:%(base_theme_scrollbar_style)s;
            $base_theme_tab_style:%(base_theme_tab_style)s;
            $base_theme_form_style:%(base_theme_form_style)s;

            
            $base_theme_sticky_tree_view:%(base_theme_sticky_tree_view)s;
            $base_theme_one2many_field_tree_view:%(base_theme_one2many_field_tree_view)s;
            $base_theme_sticky_form_view_chatter:%(base_theme_sticky_form_view_chatter)s;
            $base_theme_sticky_form_view_statusbar:%(base_theme_sticky_form_view_statusbar)s;
            
            $base_theme_separator_style:%(base_theme_separator_style)s;
            $base_theme_popup_style:%(base_theme_popup_style)s;
            $base_theme_font_size:%(base_theme_font_size)s;
            
            """ % {
            'base_theme_color_type':self.theme_color_type,
            'base_theme_primary_1_color':self.theme_primary_1_color,  
            'base_theme_primary_2_color':self.theme_primary_2_color,
            'base_theme_secondary_color':self.theme_secondary_color,                                              
            'base_theme_background_type':self.theme_background_type, 
            # 'base_theme_background_color':self.theme_background_color, 
            'base_button_type':self.button_type, 
            # 'base_button_color_type':self.button_color_type, 
            'base_button_primary_1_color':self.button_primary_1_color, 
            'base_button_primary_2_color':self.button_primary_2_color, 
            'base_button_secondary_color':self.button_secondary_color,                                     
            # 'base_is_use_google_font':self.is_use_google_font, 
            # 'base_google_font_family':self.google_font_family,
            'base_sidebr_type':self.sidebar_style,
            'base_sidebar_position':self.sidebar_position,
            'base_font_style':self.font_style,
            'base_checkbox_style':self.checkbox_style,
            'base_radion_btn_style':self.radio_btn_style,
            'base_theme_loading_type':self.theme_loading_type,
            'base_theme_scrollbar_style':self.theme_scrollbar_style,
            'base_theme_tab_style':self.theme_tab_style,
            'base_theme_form_style':self.theme_form_style,

            'base_theme_sticky_tree_view':self.base_sticky_tree_view,
            'base_theme_one2many_field_tree_view':self.base_one2many_field_tree_view,
            'base_theme_sticky_form_view_chatter':self.base_sticky_form_view_chatter,
            'base_theme_sticky_form_view_statusbar':self.base_sticky_form_view_statusbar,
            # 'base_theme_sticky_pivot_view':self.base_sticky_pivot_view,
            'base_theme_separator_style':self.theme_separator_style,
            'base_theme_popup_style':self.theme_popup_style,
            'base_theme_font_size':self.theme_font_size,
            }


            
            datas = base64.b64encode((content or "\n").encode("utf-8"))

            # Check if the file to save had already been modified
            custom_attachment = self.env["ir.attachment"].sudo().search([
            ('url','=',URL),
            ])
            if custom_attachment.sudo():
                # attachment already exist then write values.
                custom_attachment.sudo().write({"datas": datas})
            else:
                # If not, create a new attachment for theme variables scss file
                new_attach = {
                    'name': 'base_theme_variables.scss',
                    'type': "binary",
                    'mimetype': 'text/scss',
                    'datas': datas,
                    'url': URL,
                }
                self.env["ir.attachment"].sudo().create(new_attach)                
                      
        # return {
        #     'type': 'ir.actions.act_url',
        #     'target': 'self',
        #     'url': '/',
        # }         
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'target': 'self',
            }
   
      
        
