/** @tele-module **/

import { registerInstancePatchModel } from '@mail/model/model_core';

registerInstancePatchModel('mail.messaging_initializer', 'mail_bot/static/src/models/messaging_initializer/messaging_initializer.js', {
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    async _initializeTeleBot() {
        const data = await this.async(() => this.env.services.rpc({
            model: 'mail.channel',
            method: 'init_telebot',
        }));
        if (!data) {
            return;
        }
        this.env.session.telebot_initialized = true;
    },

    /**
     * @override
     */
    async start() {
        await this.async(() => this._super());

        if ('telebot_initialized' in this.env.session && !this.env.session.telebot_initialized) {
            this._initializeTeleBot();
        }
    },
});
