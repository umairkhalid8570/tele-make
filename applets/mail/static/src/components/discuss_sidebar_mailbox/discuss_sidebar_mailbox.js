/** @tele-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = twl;

export class DiscussSidebarMailbox extends Component {

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {mail.thread}
     */
    get mailbox() {
        return this.messaging.models['mail.thread'].get(this.props.threadLocalId);
    }

}

Object.assign(DiscussSidebarMailbox, {
    props: {
        threadLocalId: String,
    },
    template: 'mail.DiscussSidebarMailbox',
});

registerMessagingComponent(DiscussSidebarMailbox);
