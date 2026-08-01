#!/usr/bin/env node
"use strict";

import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync("src/MissionChief_Map_Command_Toolkit.user.js", "utf8");
const plain = value => JSON.parse(JSON.stringify(value));

function extractFunction(name) {
  const marker = "    function " + name + "(";
  const start = source.indexOf(marker);
  assert.ok(start >= 0, name + " is missing");
  const parameters = source.indexOf("(", start);
  let parameterDepth = 0;
  let brace = -1;
  for (let index = parameters; index < source.length; index += 1) {
    if (source[index] === "(") parameterDepth += 1;
    if (source[index] === ")" && --parameterDepth === 0) {
      brace = source.indexOf("{", index);
      break;
    }
  }
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
    if (char === "'" || char === '"' || char === String.fromCharCode(96)) { quote = char; continue; }
    if (char === "{") depth += 1;
    if (char === "}" && --depth === 0) return source.slice(start, index + 1);
  }
  throw new Error("Unable to extract " + name);
}

const commands = {
  menu: { label: "Toolkit Menu", action: "menu" },
  palette: { label: "Command Palette", action: "palette" },
  myMissions: { label: "Personal Missions", action: "myMissions" },
  allianceMissions: { label: "Alliance Missions", action: "allianceMissions" },
  vehicles: { label: "Vehicles", action: "vehicles" },
  buildings: { label: "Buildings", action: "buildings" },
  allianceCredits: { label: "Alliance Credits", action: "allianceCredits" },
  missionAge: { label: "Mission Age", action: "missionAge" },
  transportWatcher: { label: "Transport", action: "transportWatcher" },
  unitCommitment: { label: "Units", action: "unitCommitment" },
  vehicleCodes: { label: "Vehicle Codes", action: "vehicleCodes" },
  pressureBoard: { label: "Pressure", action: "pressureBoard" },
  clean: { label: "Clean", action: "clean" },
  markerFocus: { label: "Focus", action: "markerFocus" },
  missionPulse: { label: "Pulse", action: "missionPulse" },
  roadPriority: { label: "Roads", action: "roadPriority" },
  safeMode: { label: "Safe Mode", action: "safeMode" },
};
const defaults = {
  menu: "M", palette: "K", myMissions: "1", allianceMissions: "2", vehicles: "3", buildings: "4",
  allianceCredits: "5", missionAge: "6", transportWatcher: "7", unitCommitment: "8", vehicleCodes: "V",
  pressureBoard: "B", clean: "C", markerFocus: "F", missionPulse: "P", roadPriority: "R", safeMode: "Shift+S",
};

const sandbox = {
  console,
  Date,
  Math,
  INPUT_COMMAND_META: commands,
  DEFAULT_HOTKEY_BINDINGS: defaults,
  GESTURE_KEYS: ["swipeLeft", "swipeRight", "swipeUp", "swipeDown"],
  COMMAND_SECTION_ORDER: ["map", "missions", "finance", "locations", "appearance", "settings"],
  executed: [],
  executeInputCommand(command) { sandbox.executed.push(command); return true; },
};
vm.createContext(sandbox);
vm.runInContext(
  [
    "normaliseHotkeyBinding",
    "defaultInputStudioState",
    "normaliseInputStudioState",
    "defaultAutoHideDockState",
    "normaliseAutoHideDockState",
    "normaliseSafeModeState",
    "keyboardBindingFromEvent",
    "handleDockGesturePointerDown",
    "handleDockGesturePointerUp",
  ].map(extractFunction).join("\n") +
  "\nlet dockGestureStart=null;let state={inputStudio:defaultInputStudioState(),safeMode:{enabled:false}};" +
  "this.__probe={binding:normaliseHotkeyBinding,input:normaliseInputStudioState,dock:normaliseAutoHideDockState,safe:normaliseSafeModeState,key:keyboardBindingFromEvent,down:handleDockGesturePointerDown,up:handleDockGesturePointerUp,getState(){return state},setState(value){state=value}};",
  sandbox,
  { filename: "issue622-command-experience-runtime.js" },
);

assert.equal(sandbox.__probe.binding(" shift + s "), "Shift+S");
assert.equal(sandbox.__probe.binding("Ctrl+Alt+F12"), "Ctrl+Alt+F12");
assert.equal(sandbox.__probe.binding("Meta+K", "fallback"), "fallback");
assert.equal(sandbox.__probe.binding("Ctrl+Enter", ""), "");

const input = sandbox.__probe.input({
  hotkeys: { menu: "k", palette: "K", safeMode: "ctrl+shift+s", myMissions: "bad-key" },
  gestures: { enabled: true, swipeLeft: "safeMode", swipeRight: "unknown", swipeUp: "palette", swipeDown: "menu" },
});
assert.equal(input.hotkeys.menu, "K");
assert.equal(input.hotkeys.palette, "", "duplicate binding must fail closed");
assert.equal(input.hotkeys.myMissions, "1", "invalid binding must use the stable default");
assert.equal(input.hotkeys.safeMode, "Ctrl+Shift+S");
assert.equal(input.gestures.swipeLeft, "safeMode");
assert.equal(input.gestures.swipeRight, "menu", "unknown gesture command must use its default");
assert.equal(input.gestures.enabled, true);

assert.deepEqual(plain(sandbox.__probe.dock({ enabled: 1, edge: "horizontal" })), { enabled: true, edge: "horizontal" });
assert.deepEqual(plain(sandbox.__probe.dock({ enabled: false, edge: "diagonal" })), { enabled: false, edge: "auto" });
assert.deepEqual(plain(sandbox.__probe.safe({ enabled: true, since: "123", previousTab: "missions" })), { enabled: true, since: 123, previousTab: "missions" });
assert.equal(sandbox.__probe.safe({ previousTab: "secrets" }).previousTab, "map");
assert.equal(sandbox.__probe.key({ key: "s", ctrlKey: true, altKey: false, shiftKey: true }), "Ctrl+Shift+S");

const state = sandbox.__probe.getState();
state.inputStudio.gestures.enabled = true;
state.inputStudio.gestures.swipeRight = "palette";
let prevented = false;
sandbox.__probe.down({ pointerType: "touch", clientX: 10, clientY: 20, pointerId: 7 });
assert.equal(sandbox.__probe.up({ pointerType: "touch", clientX: 90, clientY: 24, pointerId: 7, preventDefault() { prevented = true; } }), true);
assert.deepEqual(sandbox.executed, ["palette"]);
assert.equal(prevented, true);

sandbox.__probe.down({ pointerType: "touch", clientX: 10, clientY: 20, pointerId: 8 });
assert.equal(sandbox.__probe.up({ pointerType: "touch", clientX: 30, clientY: 20, pointerId: 8, preventDefault() {} }), false, "short movement must remain a normal tap");
state.safeMode.enabled = true;
sandbox.__probe.down({ pointerType: "touch", clientX: 0, clientY: 0, pointerId: 9 });
assert.equal(sandbox.__probe.up({ pointerType: "touch", clientX: 100, clientY: 0, pointerId: 9, preventDefault() {} }), false, "Safe Mode must suppress gestures");

console.log("Issue #622 v10.1 runtime passed: hotkey validation/conflicts, state normalization, gesture thresholding and Safe Mode suppression.");
