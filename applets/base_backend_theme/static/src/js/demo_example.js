tele.define('base_backend_theme.name_of_fetures', function (require) {
    'use strict';
    var core = require('web.core');
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    ajax.loadXML('/base_backend_theme/views/base_theme_setting.xml', qweb);
    });