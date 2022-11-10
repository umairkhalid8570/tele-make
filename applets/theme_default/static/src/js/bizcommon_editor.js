tele.define('theme_default.bizcommon_editor_js', function(require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    ajax.loadXML('/theme_default/static/src/xml/bizople_theme_common.xml', qweb);
    ajax.loadXML('/theme_default/static/src/xml/button_editor.xml', qweb);
    
    options.registry.config_slider_clone_fix = options.Class.extend({
        start: function() {
            var self = this;
            startinterval()
            function startinterval() {
                var id = setInterval(frame, 100);
                function frame() {
                    var targetbtn = $('.o_legacy_dialog .modal-footer > button.btn-primary')
                    if (targetbtn.length) {
                        clicksavebtn()
                        clearInterval(id);
                    }
                }
                function clicksavebtn() {
                    $('.o_legacy_dialog .modal-footer > button.btn-primary').on('click', function() {
                        $('.bizople_product_configurator').find('[class*=container]').empty();
                        $('.bizople_brand_configurator').find('[class*=container]').empty();
                        $('.bizople_category_configurator').find('[class*=container]').empty();
                    })
                }
            }
        },
    });
    /*options.registry.oe_cat_slider = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".oe_cat_slider").empty();
            if (!editMode) {
                self.$el.find(".oe_cat_slider").on("click", _.bind(self.cat_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.oe_cat_slider').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");
                ajax.jsonRpc('/theme_default/category_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-cat-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });

    
    options.registry.second_cat_slider = options.Class.extend({
        start: function(editMode) {
            var self = this;

            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".second_cat_slider").empty();
            if (!editMode) {
                self.$el.find(".second_cat_slider").on("click", _.bind(self.cat_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.second_cat_slider').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");
                ajax.jsonRpc('/theme_default/category_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-cat-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.theme_default_product_slider = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".biz_dynamic_product_slider").empty();
            if (!editMode) {
                self.$el.find(".biz_dynamic_product_slider").on("click", _.bind(self.prod_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.prod_slider()) {
                this.prod_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            this.$target.find('.biz_dynamic_product_slider').empty();
        },

        prod_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                
                self.$modal = $(qweb.render("theme_default.bizcommon_dynamic_product_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $product_slider_cancel = self.$modal.find("#cancel"),
                    $pro_sub_data = self.$modal.find("#prod_sub_data");

                ajax.jsonRpc('/theme_default/product_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-prod-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Product Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $product_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                });
            } else {
                return;
            }
        },
    });
    options.registry.s_bizople_theme_multi_product_tab_snippet = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.oe_multi_category_slider .owl-carousel').empty();
            if (!editMode) {
                self.$el.find(".oe_multi_category_slider").on("click", _.bind(self.multi_category_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.multi_category_slider()) {
                this.multi_category_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.oe_multi_category_slider .owl-carousel').empty();
        },

        multi_category_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.multi_product_custom_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $cancel = self.$modal.find("#cancel"),
                    $snippnet_submit = self.$modal.find("#snippnet_submit");

                ajax.jsonRpc('/theme_default/product_multi_get_options', 'call', {}).then(function(res) {
                    $("select[id='slider_filter'] option").remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter']").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $snippnet_submit.on('click', function() {
                    // var type = '';
                    self.$target.attr('data-multi-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-multi-cat-slider-id', 'multi-cat-myowl' + $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        var type = '';
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        var type = '';
                        type = _t("Multi Product Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="row our-categories">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });
    options.registry.fashion_multi_cat_custom_snippet = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.fashion_multi_category_slider .owl-carousel').empty();
            if (!editMode) {
                self.$el.find(".fashion_multi_category_slider").on("click", _.bind(self.multi_category_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.multi_category_slider()) {
                this.multi_category_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.fashion_multi_category_slider .owl-carousel').empty();
        },

        multi_category_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.multi_product_custom_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $cancel = self.$modal.find("#cancel"),
                    $snippnet_submit = self.$modal.find("#snippnet_submit");

                ajax.jsonRpc('/theme_default/product_multi_get_options', 'call', {}).then(function(res) {
                    $("select[id='slider_filter'] option").remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter']").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $snippnet_submit.on('click', function() {
                    // var type = '';
                    self.$target.attr('data-multi-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-multi-cat-slider-id', 'multi-cat-myowl' + $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        var type = '';
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        var type = '';
                        type = _t("Multi Product Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="row our-categories">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });

    options.registry.health_blog_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.health_blog_slider').empty();
            
            if (!editMode) {
                self.$el.find(".health_blog_slider").on("click", _.bind(self.theme_default_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_default_blog_slider()) {
                this.theme_default_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.health_blog_slider').empty();
        },
        theme_default_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_default/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.theme_default_blog_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.bizcommon_blog_slider').empty();
           
            if (!editMode) {
                self.$el.find(".bizcommon_blog_slider").on("click", _.bind(self.theme_default_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_default_blog_slider()) {
                this.theme_default_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.bizcommon_blog_slider').empty();
        },
        theme_default_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_default/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });*/
    options.registry.s_bizople_theme_blog_slider_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_slider_owl').empty();
            
            if (!editMode) {
                self.$el.find(".blog_slider_owl").on("click", _.bind(self.theme_default_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_default_blog_slider()) {
                this.theme_default_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            this.$target.find('.blog_slider_owl').empty();
        },
        theme_default_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_default/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    /*options.registry.blog_3_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_3_custom').empty();
            
            if (!editMode) {
                self.$el.find(".blog_3_custom").on("click", _.bind(self.theme_default_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_default_blog_slider()) {
                this.theme_default_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_3_custom').empty();
        },
        theme_default_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_default/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    
    options.registry.blog_4_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_4_custom').empty();
           
            if (!editMode) {
                self.$el.find(".blog_4_custom").on("click", _.bind(self.theme_default_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_default_blog_slider()) {
                this.theme_default_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_4_custom').empty();
        },
        theme_default_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_default/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.blog_6_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_6_custom').empty();
           
            if (!editMode) {
                self.$el.find(".blog_6_custom").on("click", _.bind(self.theme_default_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_default_blog_slider()) {
                this.theme_default_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_6_custom').empty();
        },
        theme_default_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_default/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.blog_5_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_5_custom').empty();
            if (!editMode) {
                self.$el.find(".blog_5_custom").on("click", _.bind(self.theme_default_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_default_blog_slider()) {
                this.theme_default_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_5_custom').empty();
        },
        theme_default_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_default/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.blog_8_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_8_custom').empty();
            if (!editMode) {
                self.$el.find(".blog_8_custom").on("click", _.bind(self.theme_default_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.theme_default_blog_slider()) {
                this.theme_default_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_8_custom').empty();
        },
        theme_default_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_default/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.cat_slider_3 = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".cat_slider_3").empty();
            if (!editMode) {
                self.$el.find(".cat_slider_3").on("click", _.bind(self.cat_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            this.$target.find('.cat_slider_3').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");
                ajax.jsonRpc('/theme_default/category_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-cat-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.cat_slider_4 = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".cat_slider_4").empty();
            if (!editMode) {
                self.$el.find(".cat_slider_4").on("click", _.bind(self.cat_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.cat_slider_4').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");
                ajax.jsonRpc('/theme_default/category_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-cat-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });

    options.registry.brand_slider = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".brand_slider").empty();
            if (!editMode) {
                self.$el.find(".brand_slider").on("click", _.bind(self.brand_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.brand_slider()) {
                this.brand_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            this.$target.find('.brand_slider').empty();
        },

        brand_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_default.bizcommon_dynamic_brand_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $brand_slider_delete = self.$modal.find("#cancel"),
                    $pro_brand_sub_data = self.$modal.find("#brand_sub_data");
                ajax.jsonRpc('/theme_default/brand_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_brand_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-brand-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Brand Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $brand_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });*/
});