/** @tele-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = twl;

export class AttachmentList extends Component {

    /**
     * @returns {mail.attachment_list}
     */
    get attachmentList() {
        return this.messaging && this.messaging.models['mail.attachment_list'].get(this.props.attachmentListLocalId);
    }

}

Object.assign(AttachmentList, {
    props: {
        attachmentListLocalId: String,
    },
    template: 'mail.AttachmentList',
});

registerMessagingComponent(AttachmentList);
