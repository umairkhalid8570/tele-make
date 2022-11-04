tele.define('social_test_full.test_formatter_regex', function (require) {
"use strict";

var SocialPostFormatterMixin = require('social.post_formatter_mixin');

QUnit.module('Social Formatter Regex', {}, () => {
    QUnit.test('Facebook Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'facebook';
        SocialPostFormatterMixin.accountId = 42;

        const testMessage = 'Hello @[542132] Tele-Social, check this out: https://www.tele.studio #crazydeals #tele';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello",
            "<a href='/social_facebook/redirect_to_profile/42/542132?name=Tele-Social' target='_blank'>Tele-Social</a>,",
            "check this out:",
            "<a href='https://www.tele.studio' target='_blank' rel='noreferrer noopener'>https://www.tele.studio</a>",
            "<a href='https://www.facebook.com/hashtag/crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.facebook.com/hashtag/tele' target='_blank'>#tele</a>",
        ].join(' '));
    });

    QUnit.test('Instagram Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'instagram';

        const testMessage = 'Hello @Tele.Social, check this out: https://www.tele.studio #crazydeals #tele';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello",
            "<a href='https://www.instagram.com/Tele.Social' target='_blank'>@Tele.Social</a>,",
            "check this out:",
            "<a href='https://www.tele.studio' target='_blank' rel='noreferrer noopener'>https://www.tele.studio</a>",
            "<a href='https://www.instagram.com/explore/tags/crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.instagram.com/explore/tags/tele' target='_blank'>#tele</a>",
        ].join(' '));
    });

    QUnit.test('LinkedIn Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'linkedin';

        const testMessage = 'Hello, check this out: https://www.tele.studio #crazydeals #tele';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello, check this out:",
            "<a href='https://www.tele.studio' target='_blank' rel='noreferrer noopener'>https://www.tele.studio</a>",
            "<a href='https://www.linkedin.com/feed/hashtag/crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.linkedin.com/feed/hashtag/tele' target='_blank'>#tele</a>",
        ].join(' '));
    });

    QUnit.test('Twitter Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'twitter';

        const testMessage = 'Hello @Tele-Social, check this out: https://www.tele.studio #crazydeals #tele';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello",
            "<a href='https://twitter.com/Tele-Social' target='_blank'>@Tele-Social</a>,",
            "check this out:",
            "<a href='https://www.tele.studio' target='_blank' rel='noreferrer noopener'>https://www.tele.studio</a>",
            "<a href='https://twitter.com/hashtag/crazydeals?src=hash' target='_blank'>#crazydeals</a>",
            "<a href='https://twitter.com/hashtag/tele?src=hash' target='_blank'>#tele</a>",
        ].join(' '));
    });

    QUnit.test('YouTube Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'youtube';

        const testMessage = 'Hello, check this out: https://www.tele.studio #crazydeals #tele';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello, check this out:",
            "<a href='https://www.tele.studio' target='_blank' rel='noreferrer noopener'>https://www.tele.studio</a>",
            "<a href='https://www.youtube.com/results?search_query=%23crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.youtube.com/results?search_query=%23tele' target='_blank'>#tele</a>",
        ].join(' '));
    });
});

});
