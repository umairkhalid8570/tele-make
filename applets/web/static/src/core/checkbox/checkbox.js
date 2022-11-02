/** @tele-module **/

const { Component, QWeb } = twl;

/**
 * Custom checkbox
 *
 * <CheckBox
 *    value="boolean"
 *    disabled="boolean"
 *    t-on-change="_onValueChange"
 *    >
 *    Change the label text
 *  </CheckBox>
 *
 * @extends Component
 */

export class CheckBox extends Component {
    setup() {
        this.id = `checkbox-comp-${CheckBox.nextId++}`;
    }
}

CheckBox.template = "web.CheckBox";
CheckBox.nextId = 1;

QWeb.registerComponent("CheckBox", CheckBox);
