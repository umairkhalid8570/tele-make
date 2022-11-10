tele.define('base.name_of_fetures', function (require) {
    'use strict';
    var core = require('web.core');
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    ajax.loadXML('/base/views/base_theme_setting.xml', qweb);
    });