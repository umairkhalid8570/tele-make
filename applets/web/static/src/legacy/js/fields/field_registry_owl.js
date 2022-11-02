tele.define('web.field_registry_twl', function (require) {
    "use strict";

    const Registry = require('web.Registry');

    return new Registry(
        null,
        (value) => value.prototype instanceof twl.Component
    );
});

tele.define('web._field_registry_twl', function (require) {
    "use strict";

    /**
     * This module registers field components (specifications of the AbstractField Component)
     */

    const basicFields = require('web.basic_fields_twl');
    const registry = require('web.field_registry_twl');

    // Basic fields
    registry
        .add('badge', basicFields.FieldBadge)
        .add('boolean', basicFields.FieldBoolean);
});
