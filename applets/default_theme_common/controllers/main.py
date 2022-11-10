# -*- coding: utf-8 -*-
# Part of Tele Module Developed by Tele INC.
# See LICENSE file for full copyright and licensing details.

import tele
from tele import http , _
from tele.osv import expression
from tele.exceptions import UserError
import re
import math
import json
import os
import logging
import werkzeug
from werkzeug.exceptions import NotFound
from tele.addons.http_routing.models.ir_http import slug
from tele.addons.website.controllers.main import QueryURL
from tele import http, SUPERUSER_ID, fields
from tele.http import request
from tele.addons.http_routing.models.ir_http import slug, unslug
from tele.addons.website_sale.controllers import main
from tele.addons.website_sale.controllers.main import WebsiteSale
from tele.addons.website_sale.controllers.main import TableCompute
from tele.addons.sale.controllers.variant import VariantController
from tele.addons.auth_signup.controllers.main import AuthSignupHome
from tele.addons.auth_oauth.controllers.main import OAuthLogin
from tele.addons.web.controllers.main import Home
from tele.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)

class PortalUser(http.Controller):
    @http.route(['/update-image'], type='json', auth="user")
    def action_update_image(self,**post):
        datas_file = str(post['img_attachment']).split(',')
        datas_file = datas_file[1]
        user_id = request.env.user
        datas_file = ''
        if 'img_attachment' in post and post['img_attachment']:
            datas_file = str(post['img_attachment']).split(',')
            datas_file = datas_file[1]
            user_id.write({'image_1920':datas_file})
        values = {'user_id':user_id}
        return request.env['ir.ui.view']._render_template("theme_default.update_user_image",values)


class WebsiteSaleVariantController(VariantController):

    @http.route(['/product_code/get_combination_info'], type='json', auth="public", methods=['POST'], website=True)
    def get_combination_info_sku_website(self, product_template_id, product_id, combination, add_qty, **kw):
        res = self.get_combination_info(product_template_id, product_id, combination, add_qty, **kw)
        return request.env['ir.ui.view']._render_template('theme_default.product_default_code',values={'default_code': res['default_code']})

class Websitegoogle(http.Controller):

    @http.route('/theme_default/google_maps_api_key', type='json', auth='public', website=True)
    def google_maps_api_key(self):
        return json.dumps({
            'google_maps_api_key': request.website.google_maps_api_key or ''
        })
        
class WebsiteCategoyBizople(http.Controller):
    _per_page_category = 20
    _per_page_brand = 20
   
    @http.route([
        '/category',
        '/category/page/<int:page>',
        '/category/<model("product.public.category"):category_id>',
        '/category/<model("product.public.category"):category_id>/page/<int:page>'
    ], type='http', auth="public", website=True, sitemap=True)
    def product_category_data(self, page=1, category_id=None, search='', **post):
        if search:
            categories = [categ for categ in request.env['product.public.category'].search([
                ('name', 'ilike', search)]
            )]
        else:
            if category_id:
                categories = [categ for categ in request.env['product.public.category'].search([
                    ('parent_id', '=', category_id.id)]
                )]
            else:
                categories = [categ for categ in request.env['product.public.category'].search([
                    ('parent_id', '=', False)]
                )]
        if not categories and category_id:
            url = "/shop/category/%s" % slug(category_id)
            return request.redirect(url)
        else:
            pager = request.website.pager(
                url=request.httprequest.path.partition('/page/')[0],
                total=len(categories),
                page=page,
                step=self._per_page_category,
                url_args=post,
            )
            pager_begin = (page - 1) * self._per_page_category
            pager_end = page * self._per_page_category
            categories = categories[pager_begin:pager_end]
            return request.render('default_theme_common.website_sale_categoy_list_tele', {
                'categories': categories,
                'pager': pager,
                'search': search
            })

    @http.route([
        '/category-search',
    ], type='http', auth="public", website=True, sitemap=False)
    def product_category_search_data(self, **post):
        return request.redirect('/category?&search=%s' % post['search'])

    @http.route([
        '/brand',
        '/brand/page/<int:page>',
        '/brand/<model("product.brand"):brand_id>',
        '/brand/<model("product.brand"):brand_id>/page/<int:page>'
    ], type='http', auth="public", website=True, sitemap=True)
    def product_brand_data(self, page=1, brand_id=None, search='', **post):
        if search:
            brands = [brand for brand in request.env['product.brand'].search([
                ('name', 'ilike', search)]
            )]
        else:
            if brand_id:
                brands = [brand for brand in request.env['product.brand'].search([
                    ('parent_id', '=', brand_id.id)]
                )]
            else:
                brands = [brand for brand in request.env['product.brand'].search([
                    ('parent_id', '=', False)]
                )]
        if not brands and brand_id:
            url = "/shop?brand=%s" % slug(brand_id)
            return request.redirect(url)
        else:
            pager = request.website.pager(
                url=request.httprequest.path.partition('/page/')[0],
                total=len(brands),
                page=page,
                step=self._per_page_brand,
                url_args=post,
            )
            pager_begin = (page - 1) * self._per_page_brand
            pager_end = page * self._per_page_brand
            brands = brands[pager_begin:pager_end]
            return request.render('default_theme_common.website_sale_brand_list_tele', {
                'brands': brands,
                'pager': pager,
                'search': search
            })

    @http.route([
        '/brand-search',
    ], type='http', auth="public", website=True, sitemap=False)
    def brand_search_data(self, **post):
        return request.redirect('/brand?&search=%s' % post['search'])





class BizopleWebsiteSale(WebsiteSale):

    @http.route('/get_prod_quick_view_details', type='json', auth='public', website=True)
    def get_product_qv_details(self, **kw):
        product_id = int(kw.get('prod_id', 0))
        if product_id > 0:
            product = http.request.env['product.template'].search([('id', '=', product_id)])
            pricelist = request.website.get_current_pricelist()
            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
            
            return request.env['ir.ui.view']._render_template("theme_default.get_product_qv_details_template", 
                   {'product': product, 'compute_currency': compute_currency or None,})
            
        else:
            
            return request.env['ir.ui.view']._render_template("theme_default.get_product_qv_details_template", 
                   {'error': _('some problem occurred product no loaded properly')})

    # select variant popup start

    @http.route('/get_prod_select_option_details', type='json', auth='public', website=True)
    def get_product_so_details(self, **kw):
        product_id = int(kw.get('prod_id', 0))
        if product_id > 0:
            product = http.request.env['product.template'].search([('id', '=', product_id)])
            pricelist = request.website.get_current_pricelist()
            from_currency = request.env.user.company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
            
            return request.env['ir.ui.view']._render_template("theme_default.get_product_so_details_template", 
                   {'product': product, 'compute_currency': compute_currency or None,})
            
        else:
            
            return request.env['ir.ui.view']._render_template("theme_default.get_product_so_details_template", 
                   {'error': _('some problem occurred product no loaded properly')})

    # select variant popup end

    @http.route(['/shop/pager_selection/<model("product.per.page.count.tele"):pl_id>'], type='http', auth="public", website=True, sitemap=False)
    def product_page_change(self, pl_id, **post):
        request.session['default_paging_no'] = pl_id.name
        main.PPG = pl_id.name
        return request.redirect(request.httprequest.referrer or '/shop')

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>''',
        '''/shop/brands'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, brands=None, **post):
        if request.env['website'].sudo().get_current_website().theme_id.name == 'theme_default':
            add_qty = int(post.get('add_qty', 1))
            Category = request.env['product.public.category']
            if category:
                category = Category.search(
                    [('id', '=', int(category))], limit=1)
                if not category or not category.can_access_from_current_website():
                    raise NotFound()
            else:
                category = Category
            if brands:
                req_ctx = request.context.copy()
                req_ctx.setdefault('brand_id', int(brands))
                request.context = req_ctx
            result = super(BizopleWebsiteSale, self).shop(
                page=page, category=category, search=search, ppg=ppg, **post)
            page_no = request.env['product.per.page.count.tele'].sudo().search(
                [('default_active_count', '=', True)])
            if page_no:
                ppg = int(page_no.name)
            else:
                ppg = result.qcontext['ppg']

            ppr = request.env['website'].get_current_website().shop_ppr or 4

            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [[int(x) for x in v.split("-")]
                             for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}

            domain = self._get_search_domain(search, category, attrib_values)

            url = "/shop"
            if search:
                post["search"] = search
            if attrib_list:
                post['attrib'] = attrib_list
            if post:
                request.session.update(post)

            Product = request.env['product.template'].with_context(
                bin_size=True)
            session = request.session
            cate_for_price = None
            search_product = Product.search(domain)
            website_domain = request.website.website_domain()
            pricelist_context, pricelist = self._get_pricelist_context()
            categs_domain = [('parent_id', '=', False)] + website_domain
            if search:
                search_categories = Category.search(
                    [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
                categs_domain.append(('id', 'in', search_categories.ids))
            else:
                search_categories = Category
            categs = Category.search(categs_domain)

            if category:
                url = "/shop/category/%s" % slug(category)
                cate_for_price = int(category)
            prevurl = request.httprequest.referrer
            if prevurl:
                if not re.search('/shop', prevurl, re.IGNORECASE):
                    request.session['pricerange'] = ""
                    request.session['min1'] = ""
                    request.session['max1'] = ""
                    request.session['curr_category'] = ""
            brand_list = request.httprequest.args.getlist('brand')
            brand_list = [unslug(x)[1] for x in brand_list]
            brand_set = set([int(v) for v in brand_list])
            if brand_list:
                brandlistdomain = list(map(int, brand_list))
                domain += [('brand_id', 'in', brandlistdomain)]
                bran = []
                brand_obj = request.env['product.brand'].sudo().search(
                    [('id', 'in', brandlistdomain)])
                if brand_obj:
                    for vals in brand_obj:
                        if vals.name not in bran:
                            bran.append((vals.name, vals.id))
                    if bran:
                        request.session["brand_name"] = bran
            if not brand_list:
                request.session["brand_name"] = ''
            product_count = len(search_product)
            is_price_slider = request.website.viewref(
                'theme_default.default_price_slider_layout').active
            if is_price_slider:
                # For Price slider
                is_discount_hide = True if request.website.get_current_pricelist(
                ).discount_policy == 'with_discount' or request.website.get_current_pricelist(
                ).discount_policy == 'without_discount' else False
                product_slider_ids = []
                if is_discount_hide:
                    price_list = Product.search(domain).mapped('price')
                    if price_list:
                        product_slider_ids.append(min(price_list))
                        product_slider_ids.append(max(price_list))

                else:
                    asc_product_slider_ids = Product.search(
                        domain, limit=1, order='list_price')
                    desc_product_slider_ids = Product.search(
                        domain, limit=1, order='list_price desc')
                    if asc_product_slider_ids:
                        product_slider_ids.append(
                            asc_product_slider_ids.price if is_discount_hide else asc_product_slider_ids.list_price)
                    if desc_product_slider_ids:
                        product_slider_ids.append(
                            desc_product_slider_ids.price if is_discount_hide else desc_product_slider_ids.list_price)
                if product_slider_ids:
                    if post.get("range1") or post.get("range2") or not post.get("range1") or not post.get("range2"):
                        range1 = min(product_slider_ids)
                        range2 = max(product_slider_ids)
                        result.qcontext['range1'] = math.floor(range1)
                        result.qcontext['range2'] = math.ceil(range2)
                    if request.session.get('pricerange'):
                        if cate_for_price and request.session.get('curr_category') and request.session.get('curr_category') != float(cate_for_price):
                            request.session["min1"] = math.floor(range1)
                            request.session["max1"] = math.ceil(range2)

                    if session.get("min1") and session["min1"]:
                        post["min1"] = session["min1"]
                    if session.get("max1") and session["max1"]:
                        post["max1"] = session["max1"]
                    if range1:
                        post["range1"] = range1
                    if range2:
                        post["range2"] = range2
                    if range1 == range2:
                        post['range1'] = 0.0

                    if request.session.get('min1') or request.session.get('max1'):
                        if is_discount_hide:
                            price_product_list = []
                            product_withprice = Product.search(domain)
                            for prod_id in product_withprice:
                                if prod_id.price >= float(request.session['min1']) and prod_id.price <= float(request.session['max1']):
                                    price_product_list.append(prod_id.id)

                            if price_product_list:
                                domain += [('id', 'in',
                                            price_product_list)]
                            else:
                                domain += [('id', 'in', [])]
                        else:
                            domain += [('list_price', '>=', float(request.session.get('min1'))),
                                       ('list_price', '<=', float(request.session.get('max1')))]
                        request.session["pricerange"] = str(
                            request.session['min1']) + "-To-" + str(request.session['max1'])

                    if session.get('min1') and session['min1']:
                        result.qcontext['min1'] = session["min1"]
                        result.qcontext['max1'] = session["max1"]
            if cate_for_price:
                request.session['curr_category'] = float(cate_for_price)
            if request.session.get('default_paging_no'):
                ppg = int(request.session.get('default_paging_no'))
            keep = QueryURL('/shop', category=category and int(category),
                            search=search, attrib=attrib_list, order=post.get('order'))
            product_count = Product.search_count(domain)
            pager = request.website.pager(
                url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(
                domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

            ProductAttribute = request.env['product.attribute']
            if products:
                # get all products without limit
                attributes = ProductAttribute.search(
                    [('product_tmpl_ids', 'in', search_product.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)

            layout_mode = request.session.get('website_sale_shop_layout_mode')
            if not layout_mode:
                if request.website.viewref('website_sale.products_list_view').active:
                    layout_mode = 'list'
                else:
                    layout_mode = 'grid'
            active_brand_list = list(set(brand_set))

            if search:
                domain.append(("name", 'ilike', search.strip()))
            if not request.env.user.has_group('base.group_system'):
                    domain.append(("website_published", '=', True))
            product_tmpl_ids = request.env['product.template'].search(domain).ids
            
            result.qcontext.update({
                'search': search,
                'total_product_count': len(product_tmpl_ids),
                'category': category,
                'attrib_values': attrib_values,
                'attrib_set': attrib_set,
                'pager': pager,
                'pricelist': pricelist,
                'add_qty': add_qty,
                'products': products,
                'search_count': product_count,  # common for all searchbox
                'bins': TableCompute().process(products, ppg, ppr),
                'ppg': ppg,
                'ppr': ppr,
                'categories': categs,
                'attributes': attributes,
                'keep': keep,
                'search_categories_ids': search_categories.ids,
                'layout_mode': layout_mode,
                'brand_set': brand_set,
                'active_brand_list': active_brand_list,
            })
            return result
        else:
            return super(BizopleWebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)


class bizcommonSliderSettings(http.Controller):

    def get_blog_data(self, slider_filter):
        slider_header = request.env['biz.blog.slider'].sudo().search(
            [('id', '=', int(slider_filter))])
        values = {
            'slider_header': slider_header,
            'blog_slider_details': slider_header.blog_post_ids,
        }
        return values


    @http.route(['/theme_default/blog_get_options'], type='json', auth="public", website=True)
    def bizcommon_get_slider_options(self):
        slider_options = []
        option = request.env['biz.blog.slider'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options



    @http.route(['/theme_default/second_blog_get_dynamic_slider'], type='http', auth='public', website=True, sitemap=False)
    def second_get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            values = self.get_blog_data(post.get('slider-type'))
            return request.render("theme_default.bizcommon_blog_slider_view", values)

    @http.route(['/theme_default/blog_image_effect_config'], type='json', auth='public', website=True)
    def bizcommon_product_image_dynamic_slider(self, **post):
        slider_data = request.env['biz.blog.slider'].search(
            [('id', '=', int(post.get('slider_filter')))])
        values = {
            's_id': str(slider_data.no_of_objects) + '-' + str(slider_data.id),
            'counts': slider_data.no_of_objects,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values



    @http.route(['/theme_default/get_product_configurator_products'], type='http', auth='public', website=True, sitemap=False)
    def get_product_configurator_products(self, **post):
        if post.get('product_config_id'):
            product = request.env['product.template'].sudo().search([])
            values = {
                'product': product
            }
            return request.render("theme_default.product_configurator_modal_checkbox", values)

    @http.route(['/theme_default/get_category_configurator_category'], type='http', auth='public', website=True, sitemap=False)
    def get_category_configurator_category(self, **post):
        if post.get('category_config_id'):
            category = request.env['product.public.category'].sudo().search([])
            values = {
                'category': category
            }
            return request.render("theme_default.category_configurator_modal_checkbox", values)

    @http.route(['/theme_default/get_brand_configurator_brand'], type='http', auth='public', website=True, sitemap=False)
    def get_brand_configurator_brand(self, **post):
        if post.get('brand_config_id'):
            brand = request.env['product.brand'].sudo().search([])
            values = {
                'brand': brand
            }
            return request.render("theme_default.brand_configurator_modal_checkbox", values)

    @http.route(['/theme_default/get_product_configurator_grid_style'], type='http', auth='public', website=True, sitemap=False)
    def get_product_configurator_grid_style(self,limit=1, **kwargs):
        product_id = kwargs.get('product_id', False)
        product_limit = kwargs.get('product_limit', False)
        column_limit = kwargs.get('column_limit', False)
        config_title = kwargs.get('config_title', False)
        product_id = product_id.split(",")
        while("" in product_id) :
            product_id.remove("")
        while(" " in product_id) :
            product_id.remove(" ")
        product = request.env['product.template'].sudo().search([('id', 'in', product_id)], limit=int(product_limit))
        values = {
            'product_detail': product,
            'column_limit': int(column_limit),
            'config_title': config_title,
        }
        return request.render("theme_default.product_configurator_grid_style", values)

    @http.route(['/theme_default/get_category_configurator_grid_style'], type='http', auth='public', website=True, sitemap=False)
    def get_category_configurator_grid_style(self,limit=1, **kwargs):
        category_id = kwargs.get('category_id', False)
        category_limit = kwargs.get('category_limit', False)
        column_limit = kwargs.get('column_limit', False)
        config_title = kwargs.get('config_title', False)
        category_id = category_id.split(",")
        while("" in category_id) :
            category_id.remove("")
        while(" " in category_id) :
            category_id.remove(" ")
        category = request.env['product.public.category'].sudo().search([('id', 'in', category_id)], limit=int(category_limit))
        values = {
            'category_detail': category,
            'column_limit': int(column_limit),
            'config_title': config_title,
        }
        return request.render("theme_default.category_configurator_grid_style", values)

    @http.route(['/theme_default/get_brand_configurator_grid_style'], type='http', auth='public', website=True, sitemap=False)
    def get_brand_configurator_grid_style(self,limit=1, **kwargs):
        brand_id = kwargs.get('brand_id', False)
        brand_limit = kwargs.get('brand_limit', False)
        column_limit = kwargs.get('column_limit', False)
        config_title = kwargs.get('config_title', False)
        brand_id = brand_id.split(",")
        while("" in brand_id) :
            brand_id.remove("")
        while(" " in brand_id) :
            brand_id.remove(" ")
        brand = request.env['product.brand'].sudo().search([('id', 'in', brand_id)], limit=int(brand_limit))
        values = {
            'brand_detail': brand,
            'column_limit': int(column_limit),
            'config_title': config_title,
        }
        return request.render("theme_default.brand_configurator_grid_style", values)

    @http.route(['/theme_default/get_product_configurator_list_style'], type='http', auth='public', website=True, sitemap=False)
    def get_product_configurator_list_style(self,limit=1, **kwargs):
        product_id = kwargs.get('product_id', False)
        product_limit = kwargs.get('product_limit', False)
        product_id = product_id.split(",")
        config_title = kwargs.get('config_title', False)
        while("" in product_id) :
            product_id.remove("")
        while(" " in product_id) :
            product_id.remove(" ")
        product = request.env['product.template'].sudo().search([('id', 'in', product_id)], limit=int(product_limit))
        values = {
            'product_detail': product,
            'config_title': config_title,
        }
        return request.render("theme_default.product_configurator_list_style", values)

    @http.route(['/theme_default/get_category_configurator_list_style'], type='http', auth='public', website=True, sitemap=False)
    def get_category_configurator_list_style(self,limit=1, **kwargs):
        category_id = kwargs.get('category_id', False)
        category_limit = kwargs.get('category_limit', False)
        category_id = category_id.split(",")
        config_title = kwargs.get('config_title', False)
        while("" in category_id) :
            category_id.remove("")
        while(" " in category_id) :
            category_id.remove(" ")
        category = request.env['product.public.category'].sudo().search([('id', 'in', category_id)], limit=int(category_limit))
        values = {
            'category_detail': category,
            'config_title': config_title,
        }
        return request.render("theme_default.category_configurator_list_style", values)

    @http.route(['/theme_default/get_product_configurator_slider_style'], type='http', auth='public', website=True, sitemap=False)
    def get_product_configurator_slider_style(self,limit=1, **kwargs):
        product_id = kwargs.get('product_id', False)
        product_limit = kwargs.get('product_limit', False)
        config_title = kwargs.get('config_title', False)
        config_slider_description = kwargs.get('config_slider_description', False)
        product_id = product_id.split(",")
        while("" in product_id) :
            product_id.remove("")
        while(" " in product_id) :
            product_id.remove(" ")
        product = request.env['product.template'].sudo().search([('id', 'in', product_id)], limit=int(product_limit))
        values = {
            'product_detail': product,
            'config_title': config_title,
            'config_slider_description': config_slider_description,
        }
        return request.render("theme_default.product_configurator_slider_style", values)

    @http.route(['/theme_default/get_product_configurator_list_slider_style'], type='http', auth='public', website=True, sitemap=False)
    def product_configurator_list_slider_style(self,limit=1, **kwargs):
        product_id = kwargs.get('product_id', False)
        product_limit = kwargs.get('product_limit', False)
        config_title = kwargs.get('config_title', False)
        config_slider_description = kwargs.get('config_slider_description', False)
        product_id = product_id.split(",")
        while("" in product_id) :
            product_id.remove("")
        while(" " in product_id) :
            product_id.remove(" ")
        product = request.env['product.template'].sudo().search([('id', 'in', product_id)], limit=int(product_limit))
        values = {
            'product_detail': product,
            'config_title': config_title,
            'config_slider_description': config_slider_description,
        }
        return request.render("theme_default.product_configurator_list_slider_style", values)

    @http.route(['/theme_default/get_category_configurator_slider_style'], type='http', auth='public', website=True, sitemap=False)
    def get_category_configurator_slider_style(self,limit=1, **kwargs):
        category_id = kwargs.get('category_id', False)
        category_limit = kwargs.get('category_limit', False)
        config_title = kwargs.get('config_title', False)
        config_slider_description = kwargs.get('config_slider_description', False)
        category_id = category_id.split(",")
        while("" in category_id) :
            category_id.remove("")
        while(" " in category_id) :
            category_id.remove(" ")
        category = request.env['product.public.category'].sudo().search([('id', 'in', category_id)], limit=int(category_limit))
        values = {
            'category_detail': category,
            'config_title': config_title,
            'config_slider_description': config_slider_description,
        }
        return request.render("theme_default.category_configurator_slider_style", values)

    @http.route(['/theme_default/get_brand_configurator_slider_style'], type='http', auth='public', website=True, sitemap=False)
    def get_brand_configurator_slider_style(self,limit=1, **kwargs):
        brand_id = kwargs.get('brand_id', False)
        brand_limit = kwargs.get('brand_limit', False)
        config_title = kwargs.get('config_title', False)
        config_slider_description = kwargs.get('config_slider_description', False)
        brand_id = brand_id.split(",")
        while("" in brand_id) :
            brand_id.remove("")
        while(" " in brand_id) :
            brand_id.remove(" ")
        brand = request.env['product.brand'].sudo().search([('id', 'in', brand_id)], limit=int(brand_limit))
        values = {
            'brand_detail': brand,
            'config_title': config_title,
            'config_slider_description': config_slider_description,
        }
        return request.render("theme_default.brand_configurator_slider_style", values)

    @http.route(['/theme_default/get_product_banner_details_js'], type='json', auth='public', website=True)
    def get_product_banner_details_js(self, **post):
        product = request.env['product.template'].search(
            [('id', '=', int(post.get('product_id')))])
        values = {
            'product_id': product.id,
            'product_name': product.name,
            'product_description': product.description_sale,
        }
        return values

    @http.route(['/theme_default/get_product_banner_details_xml'], type='http', auth='public', website=True, sitemap=False)
    def get_product_banner_details_xml(self, **post):
        if post.get('product_id'):
            product = request.env['product.template'].sudo().search(
                [('id', '=', int(post.get('product_id')))])
            values = {
                'product': product
            }
            return request.render("theme_default.product_banner_dynamic_data", values)

    @http.route(['/theme_default/hotspot_product_select'], type='json', auth="public", website=True)
    def dynamic_hotspot_product_select(self):
        product_options = []
        option = request.env['product.template'].search([],order="name asc")
        for record in option:
            product_options.append({'id': record.id,
                                   'name': record.name})
        return product_options


    @http.route(['/theme_default/get_dynamic_hotspot_product_select'], type='http', auth='public', website=True, sitemap=False)
    def get_dynamic_hotspot_product_select(self, **post):
        if post.get('select-product-id'):
            product_info = request.env['product.template'].sudo().search(
                [('id', '=', int(post.get('select-product-id')))])
            values = {
                'product_info': product_info
            }
            # values.update({
            #     'slider_details': slider_header.product_ids,
            # })
            return request.render("theme_default.dynamic_hotspot_product_data", values)

    @http.route(['/theme_default/get_dynamic_hotspot_product_select_two'], type='json', auth='public', website=True)
    def get_dynamic_hotspot_product_select_two(self, **post):
        product_data = request.env['product.template'].search(
            [('id', '=', int(post.get('product_id')))])
        values = {
            'p_id': product_data.id,
            'p_name': product_data.name,
            'p_data': product_data,
        }
        return values

    # ajax cart popup json call
    @http.route(['/shop/cart/update_custom'], type='json', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update_custom(self, product_id, add_qty=1, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )
        return True
    
class LoginSignupPopup(Home):

    @http.route('/ajax/web/login', type='json', auth="none")
    def ajax_web_login(self, **kwargs):
        request.params['login_success'] = False
        if not request.uid:
            request.uid = tele.SUPERUSER_ID
        values = request.params.copy()
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.params
            except tele.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == tele.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')
        return values

    @http.route('/ajax/login/',type='json',auth="public")
    def ajax_login_templete(self,**kwargs):
        context = {}
        providers = OAuthLogin.list_providers(self)
        context.update(super().get_auth_signup_config())
        context.update({'providers':providers})
        signup_enabled = request.env['res.users']._get_signup_invitation_scope() == 'b2c'
        reset_password_enabled = request.env['ir.config_parameter'].sudo().get_param('auth_signup.reset_password') == 'True'
        get_temp_id = kwargs['theme_name'] + ".login_form_ajax_bizt"
        login_template = request.env['ir.ui.view']._render_template(get_temp_id,context)
        data = {'loginview':login_template}
        if(signup_enabled == True):
            get_temp_id = kwargs['theme_name'] + ".signup_form_ajax_bizt"
            signup_template = request.env['ir.ui.view']._render_template(get_temp_id,context)
            data.update({'signupview':signup_template})
        if(reset_password_enabled == True):
            get_temp_id = kwargs['theme_name'] + ".password_reset_ajax"
            reset_template = request.env['ir.ui.view']._render_template(get_temp_id,context)
            data.update({'resetview':reset_template})
        return data

    @http.route('/ajax/signup/',type="json",auth="public")
    def ajax_web_auth_signup(self,*args, **kw):
        qcontext = super(LoginSignupPopup,self).get_auth_signup_qcontext()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                super(LoginSignupPopup,self).do_signup(qcontext)
                return {'signup_success':True}
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))]):
                    qcontext['error'] = _('Another user is already registered using this email address.')
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _('Could not create a new account.')
        return qcontext

    @http.route('/ajax/web/reset_password', type='json', auth='public', website=True, sitemap=False)
    def ajax_web_auth_reset_password(self, *args, **kw):
        qcontext = super(LoginSignupPopup,self).get_auth_signup_qcontext()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                login = qcontext.get('login')
                assert login, _('No login provided.')
                _logger.info(
                    'Password reset attempt for <%s> by user <%s> from %s',
                    login, request.env.user.login, request.httprequest.remote_addr)
                request.env['res.users'].sudo().reset_password(login)
                qcontext['message'] = _('An email has been sent with credentials to reset your password')
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _('Could not reset your password')
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)
        return qcontext

class PwaMain(http.Controller):
    
    @http.route('/service_worker.js', type='http', auth="public", sitemap=False)
    def service_worker(self):
        qweb = request.env['ir.qweb'].sudo()
        website_id = request.env['website'].sudo().get_current_website().id
        languages = request.env['website'].sudo().get_current_website().language_ids
        lang_code = request.env.lang
        current_lang = request.env['res.lang']._lang_get(lang_code)
        mimetype = 'text/javascript;charset=utf-8'
        content = qweb._render('default_theme_common.service_worker', {
            'website_id': website_id,
        })
        return request.make_response(content, [('Content-Type', mimetype)])

    @http.route('/pwa/enabled', type='json', auth="public")
    def enabled_pwa(self):
        if request.env['website'].sudo().get_current_website().theme_id.name == 'theme_default':
            enabled_pwa = request.env['website'].sudo().get_current_website().enable_pwa
            if enabled_pwa:
                return enabled_pwa
    
    @http.route('/default_theme_common/manifest/<int:website_id>', type='http', auth="public", website=True, sitemap=False)
    def manifest(self, website_id=None):
        website = request.env['website'].search([('id', '=', website_id)]) if website_id else request.website
        app_name_pwa = website.app_name_pwa
        short_name_pwa = website.short_name_pwa
        description_pwa = website.description_pwa
        background_color_pwa = website.background_color_pwa
        theme_color_pwa = website.theme_color_pwa
        start_url_pwa = website.start_url_pwa
        image_192_pwa = "/web/image/website/%s/image_192_pwa/192x192" % (website.id)
        image_512_pwa = "/web/image/website/%s/image_512_pwa/512x512" % (website.id)
        
        qweb = request.env['ir.qweb'].sudo()
        mimetype = 'application/json;charset=utf-8'
        content = qweb._render('default_theme_common.manifest', {
            'app_name_pwa': app_name_pwa,
            'short_name_pwa': short_name_pwa,
            'start_url_pwa': start_url_pwa,
            'image_192_pwa': image_192_pwa,
            'image_512_pwa': image_512_pwa,
            'background_color_pwa': background_color_pwa,
            'theme_color_pwa': theme_color_pwa,
        })
        return request.make_response(content, [('Content-Type', mimetype)])
    

    @http.route('/default/search/product', type='http', auth='public', website=True, sitemap=False)
    def search_autocomplete(self, term=None, category=None, popupcateg=None):
        if category or popupcateg:
            if category:
                prod_category = request.env["product.public.category"].sudo().search([('id','=',category)])
            else:
                prod_category = request.env["product.public.category"].sudo().search([('id','=',popupcateg)])
            product_list = []
            for product in prod_category.product_tmpl_ids:
                product_list.append(product.id)
            results = request.env["product.template"].sudo().search([('name','ilike',term),('id','in',product_list)])
            value ={
                'results' :results
            }
            return request.render("theme_default.search_default",value)
        else:
            results = request.env["product.template"].sudo().search([('name','ilike',term)])
            value ={
                'results' :results
            }   
            return request.render("theme_default.search_default",value)