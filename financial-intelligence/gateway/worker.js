import { SignJWT, importPKCS8 } from 'jose';

const TOOLKIT_ORIGIN = /^https:\/\/(?:[^./]+\.)?(?:missionchief\.(?:co\.uk|com)|leitstellenspiel\.de|meldkamerspel\.com)$/iu;
const MAX_REQUEST_BYTES = 16 * 1024 * 1024;
const MAX_TRANSACTIONS = 100000;
const MAX_MONTHS = 30;
const MAX_CHECKPOINTS = 180;
const GITHUB_API = 'https://api.github.com';
let tokenCache = { token: '', expiresAt: 0 };

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const cors = corsHeaders(origin, env);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (!originAllowed(origin, env)) return json({ error: 'origin_not_allowed' }, 403, cors);

    try {
      const url = new URL(request.url);
      if (request.method === 'GET' && url.pathname === '/health') {
        return json({ ok: true, service: 'missionchief-financial-vault', schema: 1 }, 200, cors);
      }
      if (request.method === 'POST' && url.pathname === '/v1/vault/sync') {
        return await handleVaultSync(request, env, cors);
      }
      if (request.method === 'POST' && url.pathname === '/v1/benchmark') {
        return await handleBenchmark(request, env, cors);
      }
      return json({ error: 'not_found' }, 404, cors);
    } catch (error) {
      console.error(error);
      return json({ error: 'gateway_error', message: publicError(error) }, statusForError(error), cors);
    }
  }
};

function originAllowed(origin, env) {
  if (!origin) return false;
  if (TOOLKIT_ORIGIN.test(origin)) return true;
  return String(env.EXTRA_ALLOWED_ORIGINS || '').split(',').map(value => value.trim()).filter(Boolean).includes(origin);
}

function corsHeaders(origin, env) {
  const allowed = originAllowed(origin, env) ? origin : 'null';
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization,Content-Type',
    'Access-Control-Max-Age': '86400',
    'Cache-Control': 'no-store',
    'Content-Type': 'application/json; charset=utf-8',
    'Vary': 'Origin'
  };
}

function json(value, status = 200, headers = {}) {
  return new Response(JSON.stringify(value), { status, headers: { ...headers, 'Content-Type': 'application/json; charset=utf-8' } });
}

function publicError(error) {
  const message = String(error?.message || 'Unexpected gateway failure.');
  return message.length <= 240 ? message : `${message.slice(0, 239)}…`;
}

function statusForError(error) {
  if (error?.status) return error.status;
  if (error?.name === 'ValidationError') return 400;
  if (error?.name === 'AuthError') return 401;
  if (error?.name === 'ConflictError') return 409;
  return 500;
}

function fail(message, status = 400, name = 'ValidationError') {
  const error = new Error(message);
  error.status = status;
  error.name = name;
  throw error;
}

async function readJsonBody(request, maximumBytes = MAX_REQUEST_BYTES) {
  const declared = Number(request.headers.get('Content-Length') || 0);
  if (declared > maximumBytes) fail('Request body is too large.', 413);
  const text = await request.text();
  if (new TextEncoder().encode(text).byteLength > maximumBytes) fail('Request body is too large.', 413);
  try { return JSON.parse(text); } catch { fail('Request body is not valid JSON.'); }
}

function vaultKeyFromRequest(request) {
  const match = String(request.headers.get('Authorization') || '').match(/^Vault\s+([A-Za-z0-9_-]{20,180})$/u);
  if (!match) fail('A valid Financial Vault link key is required.', 401, 'AuthError');
  return match[1];
}

function normaliseText(value, maximum) {
  return String(value || '').normalize('NFKC').replace(/\s+/gu, ' ').trim().slice(0, maximum);
}

function validatePlayer(raw) {
  const id = raw?.id === undefined || raw?.id === null || raw?.id === '' ? null : normaliseText(raw.id, 64);
  const name = normaliseText(raw?.name, 120);
  if (!id && !name) fail('Player ID or player name is required.');
  return { id, name };
}

function validateTransaction(raw) {
  const timestamp = Number(raw?.timestamp);
  const amount = Math.round(Number(raw?.amount));
  const fingerprint = normaliseText(raw?.fingerprint, 120);
  const description = normaliseText(raw?.description, 500);
  if (!Number.isSafeInteger(timestamp) || timestamp < 1262304000000 || timestamp > Date.now() + 86400000) return null;
  if (!Number.isSafeInteger(amount) || amount === 0 || Math.abs(amount) > 1000000000000) return null;
  if (!fingerprint || !description) return null;
  return {
    fingerprint,
    timestamp,
    amount,
    description,
    dateLabel: normaliseText(raw?.dateLabel, 120),
    rawTimestamp: normaliseText(raw?.rawTimestamp, 80),
    sourceKey: normaliseText(raw?.sourceKey, 700),
    occurrence: Math.max(1, Math.round(Number(raw?.occurrence) || 1))
  };
}

function validateCheckpoint(raw) {
  const timestamp = Number(raw?.timestamp);
  const balance = Math.round(Number(raw?.balance));
  if (!Number.isSafeInteger(timestamp) || !Number.isSafeInteger(balance)) return null;
  return { timestamp, balance };
}

function validateVaultPayload(raw) {
  if (Number(raw?.schema) !== 1) fail('Unsupported Financial Vault schema.');
  const player = validatePlayer(raw?.player);
  const transactions = Array.isArray(raw?.transactions) ? raw.transactions.slice(0, MAX_TRANSACTIONS).map(validateTransaction).filter(Boolean) : [];
  if (Array.isArray(raw?.transactions) && raw.transactions.length > MAX_TRANSACTIONS) fail('Too many transactions.', 413);
  const balanceCheckpoints = Array.isArray(raw?.balanceCheckpoints) ? raw.balanceCheckpoints.map(validateCheckpoint).filter(Boolean).slice(-MAX_CHECKPOINTS) : [];
  return {
    schema: 1,
    player,
    deviceId: normaliseText(raw?.deviceId, 80),
    syncRevision: Math.max(0, Math.round(Number(raw?.syncRevision) || 0)),
    coverageStartMs: Number.isSafeInteger(Number(raw?.coverageStartMs)) ? Number(raw.coverageStartMs) : null,
    coverageEndMs: Number.isSafeInteger(Number(raw?.coverageEndMs)) ? Number(raw.coverageEndMs) : null,
    balanceCheckpoints,
    transactions
  };
}

function safeSlug(value, fallback = 'player') {
  const slug = normaliseText(value, 120).toLowerCase().replace(/[^a-z0-9]+/gu, '-').replace(/^-+|-+$/gu, '').slice(0, 50);
  return slug || fallback;
}

async function playerStorageKey(player) {
  if (player.id) return `id-${safeSlug(player.id, 'unknown')}-${safeSlug(player.name, 'player')}`;
  const nameHash = (await sha256Hex(player.name.toLowerCase())).slice(0, 16);
  return `name-${nameHash}-${safeSlug(player.name, 'player')}`;
}

function monthKey(timestamp) {
  return new Date(timestamp).toISOString().slice(0, 7);
}

function groupTransactionsByMonth(transactions) {
  const groups = new Map();
  for (const transaction of transactions) {
    const month = monthKey(transaction.timestamp);
    if (!groups.has(month)) groups.set(month, []);
    groups.get(month).push(transaction);
  }
  return groups;
}

function mergeTransactions(first = [], second = []) {
  const merged = new Map();
  for (const item of [...first, ...second]) {
    const valid = validateTransaction(item);
    if (valid) merged.set(valid.fingerprint, valid);
  }
  return Array.from(merged.values()).sort((a, b) => a.timestamp - b.timestamp || a.fingerprint.localeCompare(b.fingerprint));
}

function mergeCheckpoints(first = [], second = []) {
  const merged = new Map();
  for (const item of [...first, ...second]) {
    const valid = validateCheckpoint(item);
    if (valid) merged.set(`${valid.timestamp}|${valid.balance}`, valid);
  }
  return Array.from(merged.values()).sort((a, b) => a.timestamp - b.timestamp).slice(-MAX_CHECKPOINTS);
}

async function handleVaultSync(request, env, cors) {
  requireGatewayConfiguration(env);
  const syncKey = vaultKeyFromRequest(request);
  const incoming = validateVaultPayload(await readJsonBody(request));
  const playerKey = await playerStorageKey(incoming.player);
  const ownerProof = await hmacHex(env.VAULT_HMAC_SECRET, `${playerKey}|${syncKey}`);

  let lastError = null;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      const merged = await synchroniseVault(incoming, playerKey, ownerProof, env);
      return json({ ok: true, playerKey, vault: merged }, 200, cors);
    } catch (error) {
      lastError = error;
      if (error?.name !== 'ConflictError' || attempt === 2) throw error;
      await new Promise(resolve => setTimeout(resolve, 120 * (attempt + 1)));
    }
  }
  throw lastError;
}

async function synchroniseVault(incoming, playerKey, ownerProof, env) {
  const token = await githubInstallationToken(env);
  const root = `${env.GITHUB_VAULT_ROOT || 'financial-vault-data/v1'}/${playerKey}`;
  const manifestPath = `${root}/manifest.json`;
  const manifestFile = await githubReadJson(env, token, manifestPath);
  const existingManifest = manifestFile?.data || null;
  if (existingManifest?.ownerProof && !constantTimeEqual(existingManifest.ownerProof, ownerProof)) {
    fail('This player vault is linked to a different Financial Vault key.', 401, 'AuthError');
  }

  const incomingGroups = groupTransactionsByMonth(incoming.transactions);
  const months = new Set([...(Array.isArray(existingManifest?.months) ? existingManifest.months : []), ...incomingGroups.keys()]);
  const orderedMonths = Array.from(months).filter(value => /^\d{4}-\d{2}$/u.test(value)).sort().slice(-MAX_MONTHS);
  const allTransactions = [];
  const monthMetadata = [];

  for (const month of orderedMonths) {
    const monthPath = `${root}/ledger/${month}.json`;
    const existingFile = await githubReadJson(env, token, monthPath);
    const existingTransactions = Array.isArray(existingFile?.data?.transactions) ? existingFile.data.transactions : [];
    const merged = mergeTransactions(existingTransactions, incomingGroups.get(month) || []);
    if (!existingFile || merged.length !== existingTransactions.length || incomingGroups.has(month)) {
      await githubWriteJson(env, token, monthPath, { schema: 1, player: incoming.player, month, transactions: merged }, existingFile?.sha, `Sync MissionChief Financial Vault ${playerKey} ${month}`);
    }
    allTransactions.push(...merged);
    monthMetadata.push({ month, transactionCount: merged.length, firstTimestamp: merged[0]?.timestamp || null, lastTimestamp: merged.at(-1)?.timestamp || null });
  }

  const checkpoints = mergeCheckpoints(existingManifest?.balanceCheckpoints, incoming.balanceCheckpoints);
  const coverageStartValues = [incoming.coverageStartMs, existingManifest?.coverageStartMs, allTransactions[0]?.timestamp].filter(Number.isFinite);
  const coverageEndValues = [incoming.coverageEndMs, existingManifest?.coverageEndMs, allTransactions.at(-1)?.timestamp].filter(Number.isFinite);
  const syncRevision = Math.max(incoming.syncRevision, Number(existingManifest?.syncRevision) || 0) + 1;
  const manifest = {
    schema: 1,
    player: incoming.player,
    ownerProof,
    syncRevision,
    updatedAt: Date.now(),
    lastDeviceId: incoming.deviceId,
    coverageStartMs: coverageStartValues.length ? Math.min(...coverageStartValues) : null,
    coverageEndMs: coverageEndValues.length ? Math.max(...coverageEndValues) : null,
    months: orderedMonths,
    monthMetadata,
    balanceCheckpoints: checkpoints,
    transactionCount: allTransactions.length
  };
  await githubWriteJson(env, token, manifestPath, manifest, manifestFile?.sha, `Update MissionChief Financial Vault manifest ${playerKey}`);

  return {
    schema: 1,
    player: incoming.player,
    deviceId: incoming.deviceId,
    syncRevision,
    coverageStartMs: manifest.coverageStartMs,
    coverageEndMs: manifest.coverageEndMs,
    lastRemoteSyncAt: Date.now(),
    balanceCheckpoints: checkpoints,
    transactions: allTransactions
  };
}

async function handleBenchmark(request, env, cors) {
  requireGatewayConfiguration(env);
  if (String(env.BENCHMARK_ENABLED || 'true').toLowerCase() !== 'true') return json({ ok: false, disabled: true }, 202, cors);
  const raw = await readJsonBody(request, 12 * 1024);
  const submission = validateBenchmark(raw);
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const day = new Date().toISOString().slice(0, 10);
  const identity = (await hmacHex(env.VAULT_HMAC_SECRET, `${day}|${ip}`)).slice(0, 32);
  const token = await githubInstallationToken(env);
  const path = `${env.GITHUB_BENCHMARK_ROOT || 'financial-intelligence/benchmark-submissions'}/${day}/${identity}.json`;
  const existing = await githubReadJson(env, token, path);
  await githubWriteJson(env, token, path, { ...submission, receivedAt: Date.now() }, existing?.sha, `Record MissionChief benchmark ${day}`);
  return json({ ok: true }, 200, cors);
}

function validateBenchmark(raw) {
  if (Number(raw?.schema) !== 1) fail('Unsupported benchmark schema.');
  const number = (key, minimum, maximum) => {
    const value = Number(raw?.[key]);
    if (!Number.isFinite(value) || value < minimum || value > maximum) fail(`Invalid benchmark metric: ${key}.`);
    return Math.round(value * 10) / 10;
  };
  const balanceBand = normaliseText(raw?.balanceBand, 20);
  if (!['<1m', '1m-10m', '10m-50m', '50m-100m', '100m+'].includes(balanceBand)) fail('Invalid benchmark balance band.');
  return {
    schema: 1,
    toolkitVersion: normaliseText(raw?.toolkitVersion, 30),
    submittedAt: Math.round(Number(raw?.submittedAt) || Date.now()),
    balanceBand,
    periodHours: number('periodHours', 0.1, 2160),
    transactionCount: number('transactionCount', 0, 1000000),
    missionCount: number('missionCount', 0, 1000000),
    incomePerActiveHour: number('incomePerActiveHour', 0, 1000000000000),
    averageMissionReward: number('averageMissionReward', 0, 1000000000000),
    allianceIncomePercent: number('allianceIncomePercent', 0, 100),
    operatingMarginPercent: number('operatingMarginPercent', -100000, 100),
    capitalInvestmentRatioPercent: number('capitalInvestmentRatioPercent', 0, 100000),
    classificationConfidence: number('classificationConfidence', 0, 100)
  };
}

function requireGatewayConfiguration(env) {
  for (const key of ['GITHUB_APP_ID', 'GITHUB_INSTALLATION_ID', 'GITHUB_APP_PRIVATE_KEY', 'GITHUB_OWNER', 'GITHUB_REPO', 'VAULT_HMAC_SECRET']) {
    if (!env[key]) fail(`Gateway is missing required server configuration: ${key}.`, 503);
  }
}

async function githubInstallationToken(env) {
  if (tokenCache.token && tokenCache.expiresAt > Date.now() + 120000) return tokenCache.token;
  const privateKey = String(env.GITHUB_APP_PRIVATE_KEY).replace(/\\n/gu, '\n');
  const key = await importPKCS8(privateKey, 'RS256');
  const now = Math.floor(Date.now() / 1000);
  const jwt = await new SignJWT({})
    .setProtectedHeader({ alg: 'RS256' })
    .setIssuedAt(now - 60)
    .setExpirationTime(now + 540)
    .setIssuer(String(env.GITHUB_APP_ID))
    .sign(key);
  const response = await fetch(`${GITHUB_API}/app/installations/${encodeURIComponent(env.GITHUB_INSTALLATION_ID)}/access_tokens`, {
    method: 'POST',
    headers: {
      Accept: 'application/vnd.github+json',
      Authorization: `Bearer ${jwt}`,
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'MissionChief-Financial-Vault'
    }
  });
  if (!response.ok) fail(`GitHub App authentication failed with HTTP ${response.status}.`, 502);
  const data = await response.json();
  tokenCache = { token: data.token, expiresAt: Date.parse(data.expires_at) || Date.now() + 50 * 60 * 1000 };
  return tokenCache.token;
}

function githubHeaders(token) {
  return {
    Accept: 'application/vnd.github+json',
    Authorization: `Bearer ${token}`,
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'MissionChief-Financial-Vault'
  };
}

function githubContentsUrl(env, path) {
  return `${GITHUB_API}/repos/${encodeURIComponent(env.GITHUB_OWNER)}/${encodeURIComponent(env.GITHUB_REPO)}/contents/${path.split('/').map(encodeURIComponent).join('/')}?ref=${encodeURIComponent(env.GITHUB_BRANCH || 'main')}`;
}

async function githubReadJson(env, token, path) {
  const response = await fetch(githubContentsUrl(env, path), { headers: githubHeaders(token) });
  if (response.status === 404) return null;
  if (!response.ok) fail(`GitHub read failed with HTTP ${response.status}.`, 502);
  const file = await response.json();
  const text = base64ToUtf8(String(file.content || '').replace(/\s+/gu, ''));
  try { return { data: JSON.parse(text), sha: file.sha }; } catch { fail('Stored GitHub vault data is not valid JSON.', 502); }
}

async function githubWriteJson(env, token, path, data, sha, message) {
  const response = await fetch(githubContentsUrl(env, path).replace(/\?ref=.*$/u, ''), {
    method: 'PUT',
    headers: { ...githubHeaders(token), 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      content: utf8ToBase64(`${JSON.stringify(data)}\n`),
      branch: env.GITHUB_BRANCH || 'main',
      ...(sha ? { sha } : {})
    })
  });
  if (response.status === 409 || response.status === 422) fail('Concurrent vault update detected; retrying.', 409, 'ConflictError');
  if (!response.ok) fail(`GitHub write failed with HTTP ${response.status}.`, 502);
  return response.json();
}

function utf8ToBase64(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = '';
  for (let offset = 0; offset < bytes.length; offset += 0x8000) binary += String.fromCharCode(...bytes.subarray(offset, offset + 0x8000));
  return btoa(binary);
}

function base64ToUtf8(value) {
  const binary = atob(value);
  const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

async function sha256Hex(value) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(String(value)));
  return bytesToHex(new Uint8Array(digest));
}

async function hmacHex(secret, value) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(String(secret)), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const signature = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(String(value)));
  return bytesToHex(new Uint8Array(signature));
}

function bytesToHex(bytes) {
  return Array.from(bytes, byte => byte.toString(16).padStart(2, '0')).join('');
}

function constantTimeEqual(first, second) {
  const a = String(first || '');
  const b = String(second || '');
  if (a.length !== b.length) return false;
  let difference = 0;
  for (let index = 0; index < a.length; index += 1) difference |= a.charCodeAt(index) ^ b.charCodeAt(index);
  return difference === 0;
}
