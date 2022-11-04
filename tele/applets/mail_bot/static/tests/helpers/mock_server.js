/** @tele-module **/

import MockServer from 'web.MockServer';

MockServer.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _performRpc(route, args) {
        if (args.model === 'mail.channel' && args.method === 'init_telebot') {
            return this._mockMailChannelInitTeleBot();
        }
        return this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    // Private Mocked Methods
    //--------------------------------------------------------------------------

    /**
     * Simulates `init_telebot` on `mail.channel`.
     *
     * @private
     */
    _mockMailChannelInitTeleBot() {
        // TODO implement this mock task-2300480
        // and improve test "TeleBot initialized after 2 minutes"
    },
});
