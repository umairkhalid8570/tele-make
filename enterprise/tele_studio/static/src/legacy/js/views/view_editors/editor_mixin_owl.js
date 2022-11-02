tele.define('tele_studio.EditorMixinTwl', function (require) {
    "use strict";

    return Editor => class extends Editor {
        handleDrop() { }

        highlightNearestHook() { }

        setSelectable() { }

        unselectedElements() { }
    };

});
