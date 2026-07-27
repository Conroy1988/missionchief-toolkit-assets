#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "../..");
const source = fs.readFileSync(
  path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"),
  "utf8"
);
const fixture = JSON.parse(
  fs.readFileSync(
    path.join(root, ".github/fixtures/issue553-alliance-member-manager-menu.json"),
    "utf8"
  )
);

function extractFunction(name) {
  const marker = `    function ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${name} is missing`);
  const brace = source.indexOf("{", start);
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = brace; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === quote) quote = "";
      continue;
    }
    if (char === "'" || char === '"' || char === "`") {
      quote = char;
      continue;
    }
    if (char === "{") depth += 1;
    if (char === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(start, index + 1);
    }
  }
  throw new Error(`Unable to extract ${name}`);
}

const functionText = extractFunction("allianceMemberManagerMapBlockerButton");
const sandbox = {};
vm.runInNewContext(
  `${functionText}\nthis.resolveBlocker = allianceMemberManagerMapBlockerButton;`,
  sandbox
);

for (const item of fixture.cases) {
  const buttons = item.labels.map(labelText => ({
    querySelector(selector) {
      assert.equal(selector, ".mcms-label");
      return { textContent: labelText };
    },
  }));
  const panel = {
    querySelector(selector) {
      assert.match(selector, /allianceBuildingsMapBlocker/);
      return item.attributeIndex === null ? null : buttons[item.attributeIndex];
    },
    querySelectorAll(selector) {
      assert.equal(selector, ".mcms-toggle-btn");
      return buttons;
    },
  };
  const result = sandbox.resolveBlocker(panel);
  if (item.expectedIndex === null) assert.equal(result, null, item.name);
  else assert.equal(result, buttons[item.expectedIndex], item.name);
}

console.log(
  `Issue #553 menu runtime passed: ${fixture.cases.length} rendered-menu discovery cases.`
);
