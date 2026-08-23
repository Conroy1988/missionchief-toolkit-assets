#!/usr/bin/env node
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');

assert.match(source, /^\/\/ @version\s+10\.17\.2$/m);
assert.ok(source.includes("transportSweepReportState: 'mc_map_command_toolkit_transport_sweep_report_v1'"));
assert.ok(source.includes("autoIntervalMs: 60 * 1000"), 'The requested 60-second update check must remain unchanged');
assert.ok(!source.includes('scheduleTransportSweepHudDismiss'), 'The final report must not auto-dismiss');
assert.ok(source.includes('data-sweep-report-action="dismiss"'));
assert.ok(source.includes('data-action="retry-transport-sweep-discord"'));
assert.ok(source.includes('allowed_mentions: { parse: [] }'));

const finallyStart = source.indexOf("            const wasStopped = transportSweepRuntime.stopRequested;");
const finallyEnd = source.indexOf('\n        }\n    }\n\n    function stopTransportSweep', finallyStart);
assert.ok(finallyStart >= 0 && finallyEnd > finallyStart);
const finaliser = source.slice(finallyStart, finallyEnd);
assert.ok(finaliser.indexOf('createTransportSweepReport(wasStopped, missionProgress)') < finaliser.indexOf('buildTransportSweepQueue();'));
assert.ok(finaliser.indexOf('setTransportSweepReport(') < finaliser.indexOf('postTransportSweepDiscordReport(finalReport)'));

const payloadStart = source.indexOf('    function buildTransportSweepDiscordPayload(');
const payloadEnd = source.indexOf('    function operationalSitrepMissionLink(', payloadStart);
assert.ok(payloadStart >= 0 && payloadEnd > payloadStart);
const payloadSource = source.slice(payloadStart, payloadEnd);
assert.ok(!payloadSource.includes('.caption'), 'Discord sweep payload must not contain mission names');
assert.ok(!payloadSource.includes('missionId'), 'Discord sweep payload must not contain mission IDs');
for (const label of ['Missions checked', 'Eligible missions', 'Missions completed', 'Patients cleared', 'Skipped', 'Errors', 'Processed']) {
    assert.ok(payloadSource.includes(label), label);
}

const helperStart = source.indexOf('    function normaliseTransportSweepReport(');
const helperEnd = source.indexOf('    function transportSweepElementVisible(', helperStart);
assert.ok(helperStart >= 0 && helperEnd > helperStart);
const helperSource = source.slice(helperStart, helperEnd);

const storage = new Map();
const toasts = [];
let webhook = 'https://discord.com/api/webhooks/123/token';
let requestCount = 0;
const transportSweepRuntime = {
    startedAt: 1_000,
    cleared: 8,
    skipped: 2,
    errors: 0,
    processed: 10,
    missionsChecked: 14,
    lastReport: null,
    hudFinal: false,
    discordPosting: false
};
const context = vm.createContext({
    console,
    SCRIPT: { version: '10.17.2', transportSweepReportState: 'sweep-report' },
    transportSweepRuntime,
    gmGetValueSafe: (key, fallback) => storage.has(key) ? storage.get(key) : fallback,
    gmSetValueSafe: (key, value) => { storage.set(key, value); return true; },
    gmDeleteValueSafe: key => { storage.delete(key); return true; },
    getDiscordWebhookUrl: () => webhook,
    renderTransportSweepPanel: () => {},
    removeTransportSweepHud: () => {},
    showToast: message => toasts.push(message),
    discordWebhookEndpoint: () => 'https://discord.com/api/webhooks/123/token?wait=true',
    discordHttpRequest: async () => { requestCount += 1; return { status: 204, responseText: '' }; },
    sendDiscordWithRetry: async factory => factory(),
    parseDiscordError: response => `HTTP ${response?.status || 'error'}`
});
vm.runInContext(helperSource, context, { filename: 'issue689-report-helpers.js' });
vm.runInContext(payloadSource, context, { filename: 'issue689-discord-report.js' });

const baseInput = {
    schemaVersion: 1,
    sweepId: 'sweep-1700000000000-abc123',
    toolkitVersion: '10.6.0',
    startedAt: 1699999990000,
    completedAt: 1700000000000,
    durationMs: 10000,
    outcome: 'partial',
    missionsChecked: 14,
    eligibleMissions: 5,
    missionsCompleted: 5,
    cleared: 8,
    skipped: 2,
    errors: 0,
    processed: 10,
    discord: { status: 'sending', message: 'Posting', sentAt: 0 }
};
storage.set('sweep-report', JSON.stringify(baseInput));
const restored = context.loadTransportSweepReport();
assert.equal(restored.discord.status, 'failed', 'Interrupted delivery must recover as retryable');
assert.equal(restored.cleared, 8);
assert.equal(restored.successRate, 80);

const created = context.createTransportSweepReport(false, { total: 5, completed: 5 });
assert.equal(created.outcome, 'partial');
assert.equal(created.toolkitVersion, '10.17.2');
assert.equal(created.missionsChecked, 14);
assert.equal(created.discord.status, 'sending');
context.setTransportSweepReport(created, { render: false });
assert.equal(transportSweepRuntime.lastReport.sweepId, created.sweepId);
assert.ok(storage.get('sweep-report').includes(created.sweepId));

const payload = context.buildTransportSweepDiscordPayload(created);
assert.deepEqual(Array.from(payload.allowed_mentions.parse), []);
assert.equal(payload.embeds[0].color, 0xffb648);
assert.equal(payload.embeds[0].fields.find(field => field.name === 'Patients cleared').value, '8');
const serialisedPayload = JSON.stringify(payload);
assert.ok(!serialisedPayload.includes('Mission Alpha'));
assert.ok(!serialisedPayload.includes('missionId'));

(async () => {
    assert.equal(await context.postTransportSweepDiscordReport(created), true);
    assert.equal(requestCount, 1);
    assert.equal(transportSweepRuntime.lastReport.discord.status, 'sent');
    assert.equal(await context.postTransportSweepDiscordReport(transportSweepRuntime.lastReport), true);
    assert.equal(requestCount, 1, 'A sent sweep ID must never auto-post twice');

    const failedCandidate = context.normaliseTransportSweepReport({
        ...baseInput,
        sweepId: 'sweep-1700000001000-def456',
        completedAt: 1700000001000,
        outcome: 'failed',
        cleared: 0,
        skipped: 0,
        errors: 1,
        processed: 0,
        discord: { status: 'failed', message: 'Ready to retry', sentAt: 0 }
    });
    context.setTransportSweepReport(failedCandidate, { render: false });
    context.discordHttpRequest = async () => { requestCount += 1; throw new Error('Network unavailable'); };
    assert.equal(await context.postTransportSweepDiscordReport(failedCandidate, { manual: true }), false);
    assert.equal(transportSweepRuntime.lastReport.discord.status, 'failed');
    assert.match(transportSweepRuntime.lastReport.discord.message, /Network unavailable/);

    context.dismissTransportSweepReport({ quiet: true, render: false });
    assert.equal(transportSweepRuntime.lastReport, null);
    assert.equal(storage.has('sweep-report'), false);

    console.log('Issue #689 persistent Transport Sweep report runtime contract passed');
})().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
