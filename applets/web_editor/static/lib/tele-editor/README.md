# Tele editor

A fast wysiwyg editor targeting documents and website structures.

## Key features
### Unbreakable nodes
When editing some sections of a website,
there is a possibility for a selection to start or end within a node that is
contained in an unbreakable.

If the user deletes the content of the selection, the unbreakable node should not
be merged with another one.

## Demo
To open the demo page:
`http://<host:port>/web_editor/static/lib/tele-editor/demo/index.html`

## Tests
To open the test page, go to
`http://<host:port>/web_editor/static/lib/tele-editor/test/editor-test.html`

## Prettify
```bash
# install prettier
npm install -g prettier
# prettify
prettier --config '<tele-path>/applets/web_editor/static/lib/tele-editor/_prettierrc.js' --ignore-path='<tele-path>/tele/applets/web_editor/static/lib/tele-editor/_prettierignore' '<tele-path>/tele/applets/web_editor/static/lib/tele-editor/**/*.js'  --write
```

## Prettify with vscode
Install vscode extention `esbenp.prettier-vscode`.

Add the following configuration in your vscode user config or workspace config:
```
"prettier.requireConfig": true,
"prettier.configPath": "<tele-path>/tele/applets/web_editor/static/lib/tele-editor/.prettierrc.js",
"[javascript]": {
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

Then you can use the command `Format Document` or use `ctrl+h` to format a file.
