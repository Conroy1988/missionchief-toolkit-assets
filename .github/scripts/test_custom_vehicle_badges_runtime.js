#!/usr/bin/env node
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const root = path.resolve(__dirname, "../..");
const source = fs.readFileSync(path.join(root, "src/MissionChief_Map_Command_Toolkit.user.js"), "utf8");
const startMarker = "    // CUSTOM VEHICLE BADGES START";
const endMarker = "    // CUSTOM VEHICLE BADGES END";
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker, start);
assert(start >= 0 && end > start, "custom badge source block is missing");
const block = source.slice(start, end + endMarker.length);

class FakeClassList {
    constructor(owner) { this.owner = owner; this.values = new Set(); }
    add(...values) { values.forEach(value => this.values.add(String(value))); this.owner.className = Array.from(this.values).join(" "); }
    contains(value) { return this.values.has(String(value)); }
}

class FakeElement {
    constructor(tagName, ownerDocument) {
        this.nodeType = 1;
        this.tagName = String(tagName || "div").toUpperCase();
        this.ownerDocument = ownerDocument;
        this.children = [];
        this.parentElement = null;
        this.parentNode = null;
        this.attributes = new Map();
        this.dataset = {};
        this.classList = new FakeClassList(this);
        this.className = "";
        this.id = "";
        this.value = "";
        this.textContent = "";
        this.title = "";
        this.isConnected = true;
    }
    setAttribute(name, value) {
        const text = String(value);
        this.attributes.set(String(name), text);
        if (name === "id") this.id = text;
        if (name === "class") { this.className = text; text.split(/\s+/).filter(Boolean).forEach(value => this.classList.values.add(value)); }
        if (name.startsWith("data-")) {
            const key = name.slice(5).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
            this.dataset[key] = text;
        }
    }
    getAttribute(name) { return this.attributes.has(String(name)) ? this.attributes.get(String(name)) : null; }
    removeAttribute(name) {
        this.attributes.delete(String(name));
        if (String(name).startsWith("data-")) {
            const key = String(name).slice(5).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
            delete this.dataset[key];
        }
    }
    appendChild(child) {
        if (child.parentElement) child.parentElement.children = child.parentElement.children.filter(item => item !== child);
        child.parentElement = this;
        child.parentNode = this;
        child.ownerDocument ||= this.ownerDocument;
        this.children.push(child);
        return child;
    }
    insertBefore(child, before) {
        if (!before || !this.children.includes(before)) return this.appendChild(child);
        if (child.parentElement) child.parentElement.children = child.parentElement.children.filter(item => item !== child);
        child.parentElement = this;
        child.parentNode = this;
        const index = this.children.indexOf(before);
        this.children.splice(index, 0, child);
        return child;
    }
    remove() {
        if (this.parentElement) this.parentElement.children = this.parentElement.children.filter(item => item !== this);
        this.parentElement = null;
        this.parentNode = null;
        this.isConnected = false;
    }
    matches(selector) {
        return String(selector).split(",").some(raw => {
            const part = raw.trim();
            if (!part) return false;
            if (part === "label") return this.tagName === "LABEL";
            if (part === "tr") return this.tagName === "TR";
            if (part === "li") return this.tagName === "LI";
            if (part === "iframe") return this.tagName === "IFRAME";
            if (part === "frame") return this.tagName === "FRAME";
            if (part === ".vehicle_checkbox") return this.classList.contains("vehicle_checkbox");
            if (part.startsWith(".")) return this.classList.contains(part.slice(1));
            if (part === '[data-mcms-custom-vehicle-badge="1"]') return this.getAttribute("data-mcms-custom-vehicle-badge") === "1";
            if (part === "[vehicle_id]") return this.getAttribute("vehicle_id") !== null;
            if (part === "[data-vehicle-id]") return this.getAttribute("data-vehicle-id") !== null;
            if (part === "[data-vehicle_id]") return this.getAttribute("data-vehicle_id") !== null;
            if (part.startsWith('a[href*="/vehicles/"]')) return this.tagName === "A" && String(this.getAttribute("href") || "").includes("/vehicles/");
            if (part.startsWith("input")) return this.tagName === "INPUT";
            if (part.startsWith("#")) return this.id === part.slice(1);
            if (part === "[data-vehicle-caption]") return this.getAttribute("data-vehicle-caption") !== null;
            return false;
        });
    }
    closest(selector) {
        let current = this;
        while (current) {
            if (current.matches(selector)) return current;
            current = current.parentElement;
        }
        return null;
    }
    querySelectorAll(selector) {
        const result = [];
        const visit = node => {
            for (const child of node.children) {
                if (child.matches(selector)) result.push(child);
                visit(child);
            }
        };
        visit(this);
        return result;
    }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

class FakeDocument {
    constructor() {
        this.defaultView = {};
        this.documentElement = new FakeElement("html", this);
        this.head = new FakeElement("head", this);
        this.body = new FakeElement("body", this);
        this.documentElement.appendChild(this.head);
        this.documentElement.appendChild(this.body);
    }
    createElement(tag) { return new FakeElement(tag, this); }
    querySelectorAll(selector) { return this.documentElement.querySelectorAll(selector); }
    querySelector(selector) { return this.documentElement.querySelector(selector); }
    getElementById(id) { return [this.documentElement, ...this.documentElement.querySelectorAll("#" + id)].find(node => node.id === id) || null; }
}

const document = new FakeDocument();
const personalVehicleApiCache = new Map();
const cleanup = [];
const pageWindow = { __MCMS_TEST_HOOKS__: {}, MutationObserver: class { observe() {} disconnect() {} } };
const context = {
    console,
    Promise,
    Map,
    Set,
    WeakSet,
    Object,
    Array,
    String,
    Number,
    Boolean,
    Math,
    document,
    pageWindow,
    MutationObserver: pageWindow.MutationObserver,
    personalVehicleApiCache,
    customVehicleClassificationCache: new Map(),
    customVehicleClassificationRevision: -1,
    customVehicleBadgeScanTimer: null,
    customVehicleBadgeRefreshPromise: null,
    customVehicleBadgeFeatureInstalled: false,
    customVehicleBadgeObservedDocuments: new WeakSet(),
    customVehicleBadgeObservedFrames: new WeakSet(),
    vehicleDataRevision: 0,
    vehicleApiReady: true,
    vehicleApiFetchPromise: null,
    state: { uiTheme: "mapCommand", customVehicleBadges: true },
    SCRIPT: { customVehicleBadgeStyleId: "mcms-custom-vehicle-badge-style" },
    runtime: {},
    vehicleRecordId(record) { return String(record?.id ?? record?.vehicle_id ?? "") || null; },
    missionRequirementsVehicleId(element) {
        const direct = Number.parseInt(element?.value ?? element?.getAttribute?.("value") ?? element?.dataset?.vehicleId, 10);
        return Number.isFinite(direct) ? direct : -1;
    },
    refreshPersonalVehicleData() { return Promise.resolve(true); },
    runtimeClearTimeout() {},
    runtimeSetTimeout(callback) { callback(); return 1; },
    runtimeTrackObserver(observer) { return observer; },
    runtimeListen() {},
    runtimeOnCleanup(callback) { cleanup.push(callback); return callback; },
    setTimeout,
    clearTimeout,
};
vm.createContext(context);
vm.runInContext(block, context, { filename: "custom-vehicle-badges.js" });
const api = pageWindow.__MCMS_TEST_HOOKS__.customVehicleBadges;
assert(api, "test API was not exposed");

personalVehicleApiCache.set("101", { id: 101, vehicle_type: 0, vehicle_type_caption: " Railway Police Officer ", ignore_aao: true });
context.vehicleDataRevision = 1;
api.rebuildCache();
assert.deepEqual(JSON.parse(JSON.stringify(api.classificationForId("101"))), {
    vehicleId: "101",
    category: "Railway Police Officer",
    baseTypeId: 0,
    locked: true,
});

function makeRow(vehicleId) {
    const row = new FakeElement("tr", document);
    const label = new FakeElement("label", document);
    const checkbox = new FakeElement("input", document);
    checkbox.classList.add("vehicle_checkbox");
    checkbox.value = String(vehicleId);
    label.appendChild(checkbox);
    row.appendChild(label);
    document.body.appendChild(row);
    return { row, label, checkbox };
}

const specialist = makeRow(101);
let badge = api.applyRow(specialist.row);
assert(badge, "specialist badge was not rendered");
assert.equal(badge.textContent, "[Railway Police Officer]");
assert.equal(specialist.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 1);
assert.equal(specialist.row.dataset.mcmsCustomVehicleCategory, "Railway Police Officer");
assert.equal(specialist.row.dataset.mcmsCustomVehicleLocked, "true");
assert.equal(badge.parentElement, specialist.label, "badge was not placed beside the native label");

badge = api.applyRow(specialist.row);
assert.equal(specialist.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 1, "repeat scan duplicated badge");
assert.equal(badge.textContent, "[Railway Police Officer]");

personalVehicleApiCache.set("102", { id: 102, vehicle_type: 0, vehicle_type_caption: null, ignore_aao: false });
context.vehicleDataRevision = 2;
api.rebuildCache();
const ordinary = makeRow(102);
assert.equal(api.applyRow(ordinary.row), null, "ordinary IRV received a badge");
assert.equal(ordinary.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 0);

const replacement = makeRow(101);
badge = api.applyRow(replacement.row);
assert(badge, "replacement AJAX row did not receive badge");
assert.equal(replacement.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 1);

personalVehicleApiCache.set("101", { id: 101, vehicle_type: 0, vehicle_type_caption: "", ignore_aao: true });
context.vehicleDataRevision = 3;
api.rebuildCache();
assert.equal(api.applyRow(specialist.row), null, "badge remained after category removal");
assert.equal(specialist.row.querySelectorAll('[data-mcms-custom-vehicle-badge="1"]').length, 0);
assert.equal(specialist.row.dataset.mcmsCustomVehicleCategory, undefined);

console.log("Custom Vehicle Badges runtime fixtures passed");
