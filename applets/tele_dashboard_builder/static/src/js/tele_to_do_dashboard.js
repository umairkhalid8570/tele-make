tele.define('tele_dashboard_builder.tele_to_do_dashboard_filter', function (require) {
"use strict";

var TeleDashboard = require('tele_dashboard_builder.tele_dashboard');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;
var Dialog = require('web.Dialog');
var config = require('web.config');

return TeleDashboard.include({
         events: _.extend({}, TeleDashboard.prototype.events, {
        'click .tele_edit_content': '_onTeleEditTask',
        'click .tele_delete_content': '_onTeleDeleteContent',
        'click .header_add_btn': '_onTeleAddTask',
//        'click .tele_add_section': '_onTeleAddSection',
        'click .tele_li_tab': '_onTeleUpdateAddButtonAttribute',
        'click .tele_do_item_active_handler': '_onTeleActiveHandler',
    }),

        teleRenderDashboardItems: function(items) {
            var self = this;
            self.$el.find('.print-dashboard-btn').addClass("tele_pro_print_hide");
            if (self.tele_dashboard_data.tele_gridstack_config) {
                self.gridstackConfig = JSON.parse(self.tele_dashboard_data.tele_gridstack_config);
            }
            var item_view;
            var tele_container_class = 'grid-stack-item',
                tele_inner_container_class = 'grid-stack-item-content';
                for (var i = 0; i < items.length; i++) {
                if (self.grid) {

                    if (items[i].tele_dashboard_item_type === 'tele_tile') {
                        var item_view = self._teleRenderDashboardTile(items[i])
                        if (items[i].id in self.gridstackConfig) {
//                            self.grid.addWidget($(item_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 6, null, 2, 2, items[i].id);
                             if (config.device.isMobile){
                                self.grid.addWidget($(item_view)[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:true,minW:2,maxW:null,minH:2,maxH:2,id:items[i].id,});
                             }
                             else{
                                self.grid.addWidget($(item_view)[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:false,minW:2,maxW:null,minH:2,maxH:2,id:items[i].id,});
                             }
                        } else {
                             self.grid.addWidget($(item_view)[0], {x:0, y:0, w:3, h:2,autoPosition:true,minW:2,maxW:null,minH:2,maxH:2,id:items[i].id});
                        }
                    } else if (items[i].tele_dashboard_item_type === 'tele_list_view') {
                        self._renderListView(items[i], self.grid)
                    } else if (items[i].tele_dashboard_item_type === 'tele_kpi') {
                        var $kpi_preview = self.renderKpi(items[i], self.grid)
                        if (items[i].id in self.gridstackConfig) {
                            if (config.device.isMobile){
                                self.grid.addWidget($kpi_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:true,minW:2,maxW:null,minH:2,maxH:3,id:items[i].id});
                             }
                             else{
                                self.grid.addWidget($kpi_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h,autoPosition:false,minW:2,maxW:null,minH:2,maxH:3,id:items[i].id});
                             }
                        } else {
                             self.grid.addWidget($kpi_preview[0], {x:0, y:0, w:3, h:2,autoPosition:true,minW:2,maxW:null,minH:2,maxH:3,id:items[i].id});
                        }

                    }  else if (items[i].tele_dashboard_item_type === 'tele_to_do'){
                        var $to_do_preview = self.teleRenderToDoDashboardView(items[i])[0];
                        if (items[i].id in self.gridstackConfig) {
                            if (config.device.isMobile){
                                self.grid.addWidget($to_do_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h, autoPosition:true, minW:5, maxW:null, minH:2, maxH:null, id:items[i].id});
                             }
                             else{
                                self.grid.addWidget($to_do_preview[0], {x:self.gridstackConfig[items[i].id].x, y:self.gridstackConfig[items[i].id].y, w:self.gridstackConfig[items[i].id].w, h:self.gridstackConfig[items[i].id].h, autoPosition:false, minW:5, maxW:null, minH:2, maxH:null, id:items[i].id});
                             }
                        } else {
                            self.grid.addWidget($to_do_preview[0], {x:0, y:0, w:6, h:4, autoPosition:true, minW:5, maxW:null, minH:2, maxH:null, id:items[i].id})
                        }
                    } else {
                        self._renderGraph(items[i], self.grid)
                    }
                }
            }
        },

        teleRenderToDoDashboardView: function(item){
            var self = this;
            var item_title = item.name;
            var item_id = item.id;
            var list_to_do_data = JSON.parse(item.tele_to_do_data)
            var tele_header_color = self._tele_get_rgba_format(item.tele_header_bg_color);
            var tele_font_color = self._tele_get_rgba_format(item.tele_font_color);
            var tele_rgba_button_color = self._tele_get_rgba_format(item.tele_button_color);
            var $teleItemContainer = self.teleRenderToDoView(item);
            var $tele_gridstack_container = $(QWeb.render('tele_to_do_dashboard_container', {
                tele_chart_title: item_title,
                teleIsDashboardManager: self.tele_dashboard_data.tele_dashboard_manager,
                teleIsUser: true,
                tele_dashboard_list: self.tele_dashboard_data.tele_dashboard_list,
                item_id: item_id,
                to_do_view_data: list_to_do_data,
                 tele_rgba_button_color:tele_rgba_button_color,
            })).addClass('tele_dashboarditem_id')
            $tele_gridstack_container.find('.tele_card_header').addClass('tele_bg_to_color').css({"background-color": tele_header_color });
            $tele_gridstack_container.find('.tele_card_header').addClass('tele_bg_to_color').css({"color": tele_font_color + ' !important' });
            $tele_gridstack_container.find('.tele_li_tab').addClass('tele_bg_to_color').css({"color": tele_font_color + ' !important' });
            $tele_gridstack_container.find('.tele_list_view_heading').addClass('tele_bg_to_color').css({"color": tele_font_color + ' !important' });
            $tele_gridstack_container.find('.tele_to_do_card_body').append($teleItemContainer)
            return [$tele_gridstack_container, $teleItemContainer];
        },

        teleRenderToDoView: function(item, tele_tv_play=false) {
            var self = this;
            var  item_id = item.id;
            var list_to_do_data = JSON.parse(item.tele_to_do_data);
            var $todoViewContainer = $(QWeb.render('tele_to_do_dashboard_inner_container', {
                tele_to_do_view_name: "Test",
                to_do_view_data: list_to_do_data,
                item_id: item_id,
                tele_tv_play: tele_tv_play
            }));

            return $todoViewContainer
        },

        _onTeleEditTask: function(e){
            var self = this;
            var tele_description_id = e.currentTarget.dataset.contentId;
            var tele_item_id = e.currentTarget.dataset.itemId;
            var tele_section_id = e.currentTarget.dataset.sectionId;
            var tele_description = $(e.currentTarget.parentElement.parentElement).find('.tele_description').attr('value');

            var $content = "<div><input type='text' class='tele_description' value='"+ tele_description +"' placeholder='Task'></input></div>"
            var dialog = new Dialog(this, {
            title: _t('Edit Task'),
            size: 'medium',
            $content: $content,
            buttons: [
                {
                text: 'Save',
                classes: 'btn-primary',
                click: function(e){
                    var content = $(e.currentTarget.parentElement.parentElement).find('.tele_description').val();
                    if (content.length === 0){
                        content = tele_description;
                    }
                    self.onSaveTask(content, parseInt(tele_description_id), parseInt(tele_item_id), parseInt(tele_section_id));
                },
                close: true,
            },
            {
                    text: _t('Close'),
                    classes: 'btn-secondary o_form_button_cancel',
                    close: true,
                }
            ],
        });
            dialog.open();
        },

        onSaveTask: function(content, tele_description_id, tele_item_id, tele_section_id){
            var self = this;
            this._rpc({
                    model: 'tele_to.do.description',
                    method: 'write',
                    args: [tele_description_id, {
                        "tele_description": content
                    }],
                }).then(function() {
                    self.teleFetchUpdateItem(tele_item_id).then(function(){
                        $(".tele_li_tab[data-item-id=" + tele_item_id + "]").removeClass('active');
                        $(".tele_li_tab[data-section-id=" + tele_section_id + "]").addClass('active');
                        $(".tele_tab_section[data-item-id=" + tele_item_id + "]").removeClass('active');
                        $(".tele_tab_section[data-item-id=" + tele_item_id + "]").removeClass('show');
                        $(".tele_tab_section[data-section-id=" + tele_section_id + "]").addClass('active');
                        $(".tele_tab_section[data-section-id=" + tele_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + tele_item_id + "]").attr('data-section-id', tele_section_id);
                    });
                });
        },

        _onTeleDeleteContent: function(e){
            var self = this;
            var tele_description_id = e.currentTarget.dataset.contentId;
            var tele_item_id = e.currentTarget.dataset.itemId;
            var tele_section_id = e.currentTarget.dataset.sectionId;

            Dialog.confirm(this, (_t("Are you sure you want to remove this task?")), {
                confirm_callback: function() {

                    self._rpc({
                    model: 'tele_to.do.description',
                    method: 'unlink',
                    args: [parseInt(tele_description_id)],
                }).then(function() {
                        self.teleFetchUpdateItem(tele_item_id).then(function(){
                            $(".tele_li_tab[data-item-id=" + tele_item_id + "]").removeClass('active');
                            $(".tele_li_tab[data-section-id=" + tele_section_id + "]").addClass('active');
                            $(".tele_tab_section[data-item-id=" + tele_item_id + "]").removeClass('active');
                            $(".tele_tab_section[data-item-id=" + tele_item_id + "]").removeClass('show');
                            $(".tele_tab_section[data-section-id=" + tele_section_id + "]").addClass('active');
                            $(".tele_tab_section[data-section-id=" + tele_section_id + "]").addClass('show');
                            $(".header_add_btn[data-item-id=" + tele_item_id + "]").attr('data-section-id', tele_section_id);
                        });
                    });
                },
            });
        },

        _onTeleAddTask: function(e){
            var self = this;
            var tele_section_id = e.currentTarget.dataset.sectionId;
            var tele_item_id = e.currentTarget.dataset.itemId;
            var $content = "<div><input type='text' class='tele_section' placeholder='Task' required></input></div>"
            var dialog = new Dialog(this, {
            title: _t('New Task'),
            $content: $content,
            size: 'medium',
            buttons: [
                {
                text: 'Save',
                classes: 'btn-primary',
                click: function(e){
                    var content = $(e.currentTarget.parentElement.parentElement).find('.tele_section').val();
                    if (content.length === 0){
//                        this.do_notify(false, _t('Successfully sent to printer!'));
                    }
                    else{
                        self._onCreateTask(content, parseInt(tele_section_id), parseInt(tele_item_id));
                    }
                },
                close: true,
            },
            {
                    text: _t('Close'),
                    classes: 'btn-secondary o_form_button_cancel',
                    close: true,
                }
            ],
        });
            dialog.open();
        },

        _onCreateTask: function(content, tele_section_id, tele_item_id){
            var self = this;
            this._rpc({
                    model: 'tele_to.do.description',
                    method: 'create',
                    args: [{
                        tele_to_do_header_id: tele_section_id,
                        tele_description: content,
                    }],
                }).then(function() {
                    self.teleFetchUpdateItem(tele_item_id).then(function(){
                        $(".tele_li_tab[data-item-id=" + tele_item_id + "]").removeClass('active');
                        $(".tele_li_tab[data-section-id=" + tele_section_id + "]").addClass('active');
                        $(".tele_tab_section[data-item-id=" + tele_item_id + "]").removeClass('active');
                        $(".tele_tab_section[data-item-id=" + tele_item_id + "]").removeClass('show');
                        $(".tele_tab_section[data-section-id=" + tele_section_id + "]").addClass('active');
                        $(".tele_tab_section[data-section-id=" + tele_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + tele_item_id + "]").attr('data-section-id', tele_section_id);
                    });

                });
        },


        _onTeleUpdateAddButtonAttribute: function(e){
            var item_id = e.currentTarget.dataset.itemId;
            var sectionId = e.currentTarget.dataset.sectionId;
            $(".header_add_btn[data-item-id=" + item_id + "]").attr('data-section-id', sectionId);
        },

        _onTeleActiveHandler: function(e){
            var self = this;
            var tele_item_id = e.currentTarget.dataset.itemId;
            var content_id = e.currentTarget.dataset.contentId;
            var tele_task_id = e.currentTarget.dataset.contentId;
            var tele_section_id = e.currentTarget.dataset.sectionId;
            var tele_value = e.currentTarget.dataset.valueId;
            if (tele_value== 'True'){
                tele_value = false
            }else{
                tele_value = true
            }
            self.content_id = content_id;
            this._rpc({
                    model: 'tele_to.do.description',
                    method: 'write',
                    args: [content_id, {
                        "tele_active": tele_value
                    }],
                }).then(function() {
                    self.teleFetchUpdateItem(tele_item_id).then(function(){
                        $(".tele_li_tab[data-item-id=" + tele_item_id + "]").removeClass('active');
                        $(".tele_li_tab[data-section-id=" + tele_section_id + "]").addClass('active');
                        $(".tele_tab_section[data-item-id=" + tele_item_id + "]").removeClass('active');
                        $(".tele_tab_section[data-item-id=" + tele_item_id + "]").removeClass('show');
                        $(".tele_tab_section[data-section-id=" + tele_section_id + "]").addClass('active');
                        $(".tele_tab_section[data-section-id=" + tele_section_id + "]").addClass('show');
                        $(".header_add_btn[data-item-id=" + tele_item_id + "]").attr('data-section-id', tele_section_id);
                    });
                });
        }
})

});