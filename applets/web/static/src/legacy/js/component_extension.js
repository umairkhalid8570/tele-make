(function () {
    /**
     * Symbol used in ComponentWrapper to redirect Twl events to Tele legacy
     * events.
     */
    tele.widgetSymbol = Symbol('widget');

    /**
     * Add a new method to twl Components to ensure that no performed RPC is
     * resolved/rejected when the component is destroyed.
     */
    twl.Component.prototype.rpc = function () {
        return new Promise((resolve, reject) => {
            return this.env.services.rpc(...arguments)
                .then(result => {
                    if (this.__twl__.status !== 5 /* not destroyed */) {
                        resolve(result);
                    }
                })
                .catch(reason => {
                    if (this.__twl__.status !== 5) /* not destroyed */ {
                        reject(reason);
                    }
                });
        });
    };

    /**
     * Patch twl.Component.__trigger method to call a hook that adds a listener
     * for the triggered event just before triggering it. This is useful if
     * there are legacy widgets in the ancestors. In that case, there would be
     * a widgetSymbol key in the environment, corresponding to the hook to call
     * (see ComponentWrapper).
     */
    const originalTrigger = twl.Component.prototype.__trigger;
    twl.Component.prototype.__trigger = function (component, evType, payload) {
        if (this.env[tele.widgetSymbol]) {
            this.env[tele.widgetSymbol](evType);
        }
        originalTrigger.call(this, component, evType, payload);
    };
})();
