tele.define('account.ShowResequenceRenderer', function (require) {
"use strict";

const { Component } = twl;
const { useState } = twl.hooks;
const AbstractFieldTwl = require('web.AbstractFieldTwl');
const field_registry = require('web.field_registry_twl');

class ChangeLine extends Component { }
ChangeLine.template = 'account.ResequenceChangeLine';
ChangeLine.props = ["changeLine", 'ordering'];


class ShowResequenceRenderer extends AbstractFieldTwl {
    constructor(...args) {
        super(...args);
        this.data = this.value ? JSON.parse(this.value) : {
            changeLines: [],
            ordering: 'date',
        };
    }
    async willUpdateProps(nextProps) {
        await super.willUpdateProps(nextProps);
        Object.assign(this.data, JSON.parse(this.value));
    }
}
ShowResequenceRenderer.template = 'account.ResequenceRenderer';
ShowResequenceRenderer.components = { ChangeLine }

field_registry.add('account_resequence_widget', ShowResequenceRenderer);
return ShowResequenceRenderer;
});
