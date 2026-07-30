#!/usr/bin/env node
"use strict";

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { instrumentSource } from "./build-render-probe-userscript.mjs";

export const CAPTURE_PROFILE = "issue247-v832-live-performance";
export const REQUIRED_SCENARIOS = Object.freeze([
  ["idle-map", "Leave the map idle for at least 20 seconds."],
  ["settings-open-close", "Open and close Toolkit Settings five times, changing no settings."],
  ["mission-open-close", "Open and close at least three active mission windows."],
  ["unit-selection", "Open a mission and select/deselect several vehicles without dispatching."],
  ["map-pan-zoom", "Pan the map repeatedly and zoom in/out several levels."],
  ["layout-change", "Resize the browser or change orientation/Tablet layout, then restore it."],
]);

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function stripUserscriptMetadata(source) {
  const marker = "// ==/UserScript==";
  const end = source.indexOf(marker);
  if (end < 0) throw new Error("Profiler metadata terminator not found");
  return source.slice(end + marker.length).replace(/^\s+/u, "");
}

function metadataValue(source, name) {
  const match = source.match(new RegExp(`^//\\s*@${name}\\s+([^\\n]+)$`, "mu"));
  return match?.[1]?.trim() || null;
}

function replaceMetadata(source, name, value) {
  const pattern = new RegExp(`^//\\s*@${name}\\s+[^\\n]+$`, "mu");
  if (!pattern.test(source)) throw new Error(`Missing metadata field: ${name}`);
  return source.replace(pattern, `// @${name.padEnd(12)} ${value}`);
}

function captureGuideSource() {
  return `
(function installMcmsCaptureGuide() {
    'use strict';
    const profile = ${JSON.stringify(REQUIRED_SCENARIOS)};
    const profiler = globalThis.__MCMS_PROFILER__;
    if (!profiler) throw new Error('MCMS capture profiler failed to initialise');
    let index = 0;
    profiler.setScenario(profile[0][0]);
    profiler.start();

    function installGuide() {
        const panel = document.getElementById('mcms-development-profiler');
        if (!panel || panel.querySelector('[data-mcms-capture-guide]')) return;
        const guide = document.createElement('section');
        guide.dataset.mcmsCaptureGuide = 'true';
        guide.style.cssText = 'flex:1 1 100%;border-top:1px solid #555;padding-top:7px;display:grid;gap:5px';
        const warning = document.createElement('strong');
        warning.style.color = '#ffcf66';
        warning.textContent = 'Capture bundle active — keep the normal Toolkit userscript disabled during this session.';
        const stage = document.createElement('span');
        const instruction = document.createElement('span');
        instruction.style.color = '#d8e7ef';
        const controls = document.createElement('div');
        controls.style.cssText = 'display:flex;gap:6px;flex-wrap:wrap';
        const next = document.createElement('button');
        const restart = document.createElement('button');
        for (const button of [next, restart]) {
            button.type = 'button';
            button.style.cssText = 'font:inherit;padding:5px 8px;cursor:pointer';
        }
        restart.textContent = 'Restart capture';

        function sync() {
            const [name, text] = profile[index];
            profiler.setScenario(name);
            const selector = panel.querySelector('select[aria-label="Profiler scenario"]');
            if (selector) selector.value = name;
            const status = panel.querySelector('strong');
            if (status) status.textContent = 'Profiler running · ' + name;
            stage.textContent = 'Stage ' + (index + 1) + '/' + profile.length + ': ' + name;
            instruction.textContent = text;
            next.textContent = index === profile.length - 1 ? 'Finish and export report' : 'Mark complete — next stage';
        }

        next.addEventListener('click', () => {
            if (index < profile.length - 1) {
                index += 1;
                sync();
                return;
            }
            profiler.stop();
            const status = panel.querySelector('strong');
            if (status) status.textContent = 'Profiler stopped · capture complete';
            stage.textContent = 'Capture complete';
            instruction.textContent = 'Save the downloaded JSON report and upload it for validation.';
            next.disabled = true;
            profiler.export();
        });
        restart.addEventListener('click', () => {
            profiler.reset();
            index = 0;
            profiler.setScenario(profile[0][0]);
            profiler.start();
            next.disabled = false;
            sync();
        });
        controls.append(next, restart);
        guide.append(warning, stage, instruction, controls);
        panel.appendChild(guide);
        sync();
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', installGuide, { once: true });
    else installGuide();
})();
`;
}

export function buildCaptureBundle(toolkitSource, profilerSource) {
  const toolkitVersion = metadataValue(toolkitSource, "version");
  if (!toolkitVersion) throw new Error("Toolkit version missing");
  const canonicalSourceSha256 = sha256(toolkitSource);
  const profilerVersion = metadataValue(profilerSource, "version");
  if (!profilerVersion) throw new Error("Profiler version missing");

  const instrumented = instrumentSource(toolkitSource);
  let bundle = instrumented.generated;
  bundle = replaceMetadata(bundle, "name", `MissionChief Toolkit v${toolkitVersion} Authenticated Performance Capture`);
  bundle = replaceMetadata(bundle, "namespace", "https://github.com/Conroy1988/missionchief-toolkit-assets/performance-capture");
  bundle = replaceMetadata(bundle, "version", `${toolkitVersion}-capture.1`);
  bundle = replaceMetadata(bundle, "description", "Development-only authenticated MissionChief performance capture. Disable the stable Toolkit while installed.");
  bundle = bundle.replace(/^//\s*@(?:downloadURL|updateURL)\s+[^\n]+\n?/gmu, "");

  let profilerBody = stripUserscriptMetadata(profilerSource);
  const startupAnchor = "getStartupMetrics: () => window.__MCMS_STARTUP_METRICS__ || {},";
  if ((profilerBody.match(new RegExp(startupAnchor.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gu")) || []).length !== 1) {
    throw new Error("Profiler startup-metrics anchor drifted");
  }
  profilerBody = profilerBody.replace(
    startupAnchor,
    `getStartupMetrics: () => ({ ...(window.__MCMS_STARTUP_METRICS__ || {}), captureProfile: ${JSON.stringify(CAPTURE_PROFILE)}, captureToolkitVersion: ${JSON.stringify(toolkitVersion)}, captureSourceSha256: ${JSON.stringify(canonicalSourceSha256)}, captureProfilerVersion: ${JSON.stringify(profilerVersion)} }),`,
  );

  const metadataEndMarker = "// ==/UserScript==";
  const metadataEnd = bundle.indexOf(metadataEndMarker);
  if (metadataEnd < 0) throw new Error("Generated Toolkit metadata terminator missing");
  const insertion = metadataEnd + metadataEndMarker.length;
  const prelude = `\n// Development capture profile: ${CAPTURE_PROFILE}\n${profilerBody}\n${captureGuideSource()}\n`;
  bundle = bundle.slice(0, insertion) + prelude + bundle.slice(insertion);

  if (/^\/\/\s*@(downloadURL|updateURL)\s+/mu.test(bundle)) throw new Error("Capture bundle must not carry stable update URLs");
  if (!bundle.includes("globalThis.__MCMS_PROFILER__?.beginRender?.(\"updateUI\")")) throw new Error("updateUI probe missing");
  if (!bundle.includes("globalThis.__MCMS_PROFILER__?.beginRender?.(\"renderOperationalPanels\")")) throw new Error("operational render probe missing");
  if (!bundle.includes(canonicalSourceSha256)) throw new Error("Canonical source authority missing from capture bundle");

  return {
    bundle,
    manifest: {
      schemaVersion: 1,
      profile: CAPTURE_PROFILE,
      toolkitVersion,
      canonicalSourceSha256,
      profilerVersion,
      profilerSourceSha256: sha256(profilerSource),
      bundleSha256: sha256(bundle),
      instrumentedFunctions: instrumented.targets,
      requiredScenarios: REQUIRED_SCENARIOS.map(([name]) => name),
      stableUpdateUrlsRemoved: true,
      productionSourceModified: false,
      requiresStableToolkitDisabled: true,
    },
  };
}

function parseArgs(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) throw new Error(`Unexpected argument: ${key}`);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) throw new Error(`Missing value for ${key}`);
    result[key.slice(2)] = value;
    index += 1;
  }
  return result;
}

function instructions(manifest, bundleName) {
  return `# MissionChief Toolkit authenticated performance capture\n\n` +
    `- Toolkit authority: **v${manifest.toolkitVersion}**\n` +
    `- Canonical source SHA-256: \`${manifest.canonicalSourceSha256}\`\n` +
    `- Capture bundle SHA-256: \`${manifest.bundleSha256}\`\n\n` +
    `## One controlled session\n\n` +
    `1. Disable the normal MissionChief Map Command Toolkit userscript.\n` +
    `2. Install \`${bundleName}\`. It has a separate identity and no update URL.\n` +
    `3. Reload MissionChief. The profiler starts automatically on **idle-map**.\n` +
    `4. Follow the six stages displayed in the bottom-right capture panel.\n` +
    `5. Press **Finish and export report**.\n` +
    `6. Remove/disable the capture bundle and re-enable the stable Toolkit.\n` +
    `7. Upload the exported \`mcms-performance-*.json\` report for validation.\n\n` +
    `The capture collects aggregate timing, mutation and runtime-resource counts only. It does not collect mission titles, addresses, coordinates, vehicle/personnel names, alliance messages, cookies, storage values or webhook contents.\n`;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  for (const required of ["source", "profiler", "output", "manifest", "instructions"]) {
    if (!args[required]) throw new Error(`Missing --${required}`);
  }
  const toolkitPath = path.resolve(args.source);
  const profilerPath = path.resolve(args.profiler);
  const outputPath = path.resolve(args.output);
  const manifestPath = path.resolve(args.manifest);
  const instructionsPath = path.resolve(args.instructions);
  if ([profilerPath, manifestPath, instructionsPath].includes(outputPath)) throw new Error("Capture output paths must be distinct");
  const toolkitSource = fs.readFileSync(toolkitPath, "utf8");
  const profilerSource = fs.readFileSync(profilerPath, "utf8");
  const result = buildCaptureBundle(toolkitSource, profilerSource);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
  fs.mkdirSync(path.dirname(instructionsPath), { recursive: true });
  fs.writeFileSync(outputPath, result.bundle, "utf8");
  fs.writeFileSync(manifestPath, JSON.stringify(result.manifest, null, 2) + "\n", "utf8");
  fs.writeFileSync(instructionsPath, instructions(result.manifest, path.basename(outputPath)), "utf8");
  console.log(JSON.stringify(result.manifest, null, 2));
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname)) {
  try { main(); } catch (error) { console.error(error.stack || error.message); process.exit(1); }
}
