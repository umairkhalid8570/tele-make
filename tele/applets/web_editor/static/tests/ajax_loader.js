tele.define('web_editor.ajax.loader', function (require) {
'use strict';

const loaderFunctions = require('web_editor.loader');

loaderFunctions.createWysiwyg = (parent, options) => {
  const Wysiwyg = tele.__DEBUG__.services['web_editor.wysiwyg'];
  return new Wysiwyg(parent, options);
};

});
