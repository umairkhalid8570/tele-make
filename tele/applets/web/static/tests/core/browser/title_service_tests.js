/** @tele-module **/

import { titleService } from "@web/core/browser/title_service";
import { registry } from "@web/core/registry";
import { makeTestEnv } from "../../helpers/mock_env";

// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

let env;
let title;

QUnit.module("Title", {
    async beforeEach() {
        title = document.title;
        registry.category("services").add("title", titleService);
        env = await makeTestEnv();
    },
    afterEach() {
        document.title = title;
    },
});

QUnit.test("simple title", async (assert) => {
    assert.expect(1);
    env.services.title.setParts({ ztele: "Tele" });
    assert.strictEqual(env.services.title.current, "Tele");
});

QUnit.test("add title part", async (assert) => {
    assert.expect(2);
    env.services.title.setParts({ ztele: "Tele", chat: null });
    assert.strictEqual(env.services.title.current, "Tele");
    env.services.title.setParts({ action: "Import" });
    assert.strictEqual(env.services.title.current, "Tele - Import");
});

QUnit.test("modify title part", async (assert) => {
    assert.expect(2);
    env.services.title.setParts({ ztele: "Tele" });
    assert.strictEqual(env.services.title.current, "Tele");
    env.services.title.setParts({ ztele: "Ztele" });
    assert.strictEqual(env.services.title.current, "Ztele");
});

QUnit.test("delete title part", async (assert) => {
    assert.expect(2);
    env.services.title.setParts({ ztele: "Tele" });
    assert.strictEqual(env.services.title.current, "Tele");
    env.services.title.setParts({ ztele: null });
    assert.strictEqual(env.services.title.current, "");
});

QUnit.test("all at once", async (assert) => {
    assert.expect(2);
    env.services.title.setParts({ ztele: "Tele", action: "Import" });
    assert.strictEqual(env.services.title.current, "Tele - Import");
    env.services.title.setParts({ action: null, ztele: "Ztele", chat: "Sauron" });
    assert.strictEqual(env.services.title.current, "Ztele - Sauron");
});

QUnit.test("get title parts", async (assert) => {
    assert.expect(3);
    env.services.title.setParts({ ztele: "Tele", action: "Import" });
    assert.strictEqual(env.services.title.current, "Tele - Import");
    const parts = env.services.title.getParts();
    assert.deepEqual(parts, { ztele: "Tele", action: "Import" });
    parts.action = "Export";
    assert.strictEqual(env.services.title.current, "Tele - Import"); // parts is a copy!
});
