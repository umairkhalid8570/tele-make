/** @tele-module **/

import { afterEach, beforeEach, start } from '@mail/utils/test_utils';

QUnit.module('mail_bot', {}, function () {
QUnit.module('models', {}, function () {
QUnit.module('messaging_initializer', {}, function () {
QUnit.module('messaging_initializer_tests.js', {
    beforeEach() {
        beforeEach(this);

        this.start = async params => {
            const { env, widget } = await start(Object.assign({}, params, {
                data: this.data,
            }));
            this.env = env;
            this.widget = widget;
        };
    },
    afterEach() {
        afterEach(this);
    },
});


QUnit.test('TeleBot initialized at init', async function (assert) {
    // TODO this test should be completed in combination with
    // implementing _mockMailChannelInitTeleBot task-2300480
    assert.expect(2);

    await this.start({
        env: {
            session: {
                telebot_initialized: false,
            },
        },
        async mockRPC(route, args) {
            if (args.method === 'init_telebot') {
                assert.step('init_telebot');
            }
            return this._super(...arguments);
        },
    });

    assert.verifySteps(
        ['init_telebot'],
        "should have initialized TeleBot at init"
    );
});

});
});
});
