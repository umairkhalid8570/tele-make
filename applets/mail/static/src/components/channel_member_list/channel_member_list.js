/** @tele-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = twl;

export class ChannelMemberList extends Component {

    /**
     * @returns {mail.thread}
     */
    get channel() {
        return this.messaging.models['mail.thread'].get(this.props.channelLocalId);
    }

}

Object.assign(ChannelMemberList, {
    props: {
        channelLocalId: String,
    },
    template: 'mail.ChannelMemberList',
});

registerMessagingComponent(ChannelMemberList);
